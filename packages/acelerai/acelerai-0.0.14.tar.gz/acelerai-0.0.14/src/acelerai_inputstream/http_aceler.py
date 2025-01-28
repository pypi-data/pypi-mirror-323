import asyncio
from datetime import datetime
import gzip
import hashlib
import json
import os
import struct
import httpx
from httpx import Response
import msgpack
import requests
from acelerai_inputstream import DATA_URL, INPUTSTREAM_URL, QUERY_MANAGER, VERIFY_HTTPS
from acelerai_inputstream.inputstream import INSERTION_MODE, Inputstream
from acelerai_inputstream.utils import CustomJSONEncoder, CustomJsonDecoder, custom_encoder, decode_datetime

# Type conversion
from decimal import Decimal
from datetime import datetime, date, time
from uuid import UUID

import logging
logger = logging.getLogger("HttpAcelerAI")

SEM = asyncio.Semaphore(20)  # Limitar concurrencia a 20 conexiones
MAX_RETRIES = 5  # Número máximo de reintentos
INITIAL_BACKOFF = 1  # Tiempo inicial de espera en segundos
BACKOFF_MULTIPLIER = 2  # Factor multiplicador para el tiempo de espera

packer = msgpack.Packer(default=custom_encoder) 


class AcelerAIHttpClient():

    def __init__(self, token:str):
        self.token = token
        self.lock = asyncio.Lock()


    def get_inputstream_by_ikey(self, ikey:str) -> Inputstream:
        try:
            headers = { "Authorization": f"A2G {self.token}"}

            res = requests.get(INPUTSTREAM_URL + f"/Inputstream/Ikey/{ikey}", headers=headers, verify=VERIFY_HTTPS)
            if res.status_code != 200:
                if res.status_code == 404: raise Exception("Inputstream not found, please check your ikey")
                if res.status_code == 401: raise Exception("Unauthorized: please check your token or access permissions")
                if res.status_code == 403: raise Exception("Forbidden: please check your access permissions")
                raise Exception(f"Error getting inputstream, {res.status_code} {res.text}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return Inputstream(from_response=True, **content["data"])
        except Exception as e:
            raise e
        

    async def _write_to_file(self, ikey:str, query, data:list[dict]) -> None:

        if not os.path.exists(f".acelerai_cache/")               : os.mkdir(f".acelerai_cache/")
        if not os.path.exists(f".acelerai_cache/data/")          : os.mkdir(f".acelerai_cache/data/")
        if not os.path.exists(f".acelerai_cache/data/{ikey}/")   : os.mkdir(f".acelerai_cache/data/{ikey}/")

        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()

        # save data
        file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"

        async with self.lock:  # Garantiza que solo una tarea escriba a la vez
            with open(file_name, "ab") as file:
                for record in data:
                    file.write(packer.pack(record))


    async def fetch_bigpage(self, ikey: str, query: dict):
        async with SEM:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            my_body = { "query": json.dumps(query, cls=CustomJSONEncoder) }

            buffer = b""  # Buffer para ensamblar datos incompletos
            timeout = httpx.Timeout(10800.0, connect=10.0, read=10800.0)
            retries = 0
            backoff = INITIAL_BACKOFF

            while retries < MAX_RETRIES:
                try:
                    logger.info(f"Downloading data on retry {retries}")
                    async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                        async with client.stream(
                            "POST",
                            f"{QUERY_MANAGER}/QueryData/Find",
                            json=my_body,
                            headers=headers,
                            params={"page": 0, "page_size": 0}
                        ) as response:

                            if response.status_code != 200:
                                msg = ''
                                async for chunk in response.aiter_bytes():
                                    if chunk:
                                        msg += chunk.decode("utf-8")
                                raise Exception(f"{response.status_code} {msg}")

                            rows_count = 0
                            async for chunk in response.aiter_bytes():
                                buffer += chunk  # Agregar los datos al buffer
                                while len(buffer) >= 4:  # Asegurarse de que al menos 4 bytes están disponibles
                                    obj_length = struct.unpack(">I", buffer[:4])[0]

                                    if len(buffer) < 4 + obj_length:
                                        break  # Esperar más datos si el objeto no está completo

                                    obj_data = buffer[4:4 + obj_length]
                                    buffer = buffer[4 + obj_length:]  # Actualizar el buffer
                                    decompressed_data = gzip.decompress(obj_data)  # Descomprimir los datos
                                    data = msgpack.unpackb(decompressed_data, object_hook=decode_datetime)  # Deserializar el objeto
                                    rows_count += len(data)
                                    if rows_count % 20000 == 0: logger.info(f"Downloaded {rows_count} rows")

                                    # Procesar y guardar los datos
                                    await self._write_to_file(ikey, query, data)
                    logger.info(f"Downloaded data on retry {retries}")
                    break  # Si todo va bien, salimos del bucle
                except (httpx.StreamError, httpx.ConnectError, httpx.ReadTimeout) as e:
                    # Manejar errores específicos de conexión y reinicio
                    retries += 1
                    if retries >= MAX_RETRIES:
                        raise Exception(f"Max retries exceeded: {e}")
                    logger.warning(f"Error: {e}. Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER  # Incrementar el tiempo de espera exponencialmente


    async def fetch_page(self, ikey: str, query: dict, delete_id: bool = True, page: int = 1, page_size: int = 1000):
        async with SEM:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            my_body = {
                "delete_id": delete_id,
                "query": json.dumps(query, cls=CustomJSONEncoder)
            }

            buffer = b""  # Buffer para ensamblar datos incompletos
            timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
            retries = 0
            backoff = INITIAL_BACKOFF

            while retries < MAX_RETRIES:
                try:
                    logger.info(f"Downloading page {page} on retry {retries}")
                    async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                        async with client.stream(
                            "POST",
                            f"{QUERY_MANAGER}/QueryData/Find",
                            json=my_body,
                            headers=headers,
                            params={"page": page, "page_size": page_size}
                        ) as response:

                            if response.status_code != 200:
                                msg = ''
                                async for chunk in response.aiter_bytes():
                                    if chunk:
                                        msg += chunk.decode("utf-8")
                                raise Exception(f"{response.status_code} {msg}")

                            async for chunk in response.aiter_bytes():
                                buffer += chunk  # Agregar los datos al buffer
                                while len(buffer) >= 4:  # Asegurarse de que al menos 4 bytes están disponibles
                                    obj_length = struct.unpack(">I", buffer[:4])[0]

                                    if len(buffer) < 4 + obj_length:
                                        break  # Esperar más datos si el objeto no está completo

                                    obj_data = buffer[4:4 + obj_length]
                                    buffer = buffer[4 + obj_length:]  # Actualizar el buffer
                                    decompressed_data = gzip.decompress(obj_data)  # Descomprimir los datos
                                    data = msgpack.unpackb(decompressed_data, object_hook=decode_datetime)  # Deserializar el objeto

                                    # Procesar y guardar los datos
                                    await self._write_to_file(ikey, query, data)
                    logger.info(f"Downloaded page {page} on retry {retries}")
                    break  # Si todo va bien, salimos del bucle
                except (httpx.StreamError, httpx.ConnectError, httpx.ReadTimeout) as e:
                    # Manejar errores específicos de conexión y reinicio
                    retries += 1
                    if retries >= MAX_RETRIES:
                        raise Exception(f"Max retries exceeded: {e}")
                    logger.warning(f"Error: {e}. Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER  # Incrementar el tiempo de espera exponencialmente
                
                except Exception as e:
                    logger.error(f"An error occurred: {e}", exc_info=True)
                    raise e


    async def find_one(self, ikey:str, query:dict) -> bool:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                res = await client.post(f"{QUERY_MANAGER}/QueryData/FindOne", 
                    data=json.dumps(query, cls=CustomJSONEncoder),
                    headers=headers
                )

            if res.status_code != 200:
                raise Exception(f"Error getting inputstream data {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            await self._write_to_file(ikey, query, [content["data"]])
            return True
            
        except Exception as e:
            raise False


    async def fetch_page_agg(self, client: httpx.AsyncClient, ikey: str, pipeline:list[dict], page, page_size):
        
        logger.info(f"Downloading page {page}")
        async with SEM:
            res = await client.post(
                f"{QUERY_MANAGER}/QueryData/Aggregate",
                params = {"page": page, "page_size": page_size},
                data = json.dumps(pipeline, cls=CustomJSONEncoder)
            )

            logger.info(f"Code Res: {res.status_code}")
            if res.status_code != 200: raise Exception(f"Error getting inputstream data {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            
            await self._write_to_file(ikey, pipeline, content["data"])
            logger.info(f"Downloaded page {page}")


    async def aggregate(self, ikey:str, pipeline:list[dict]) -> bool:
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            res = requests.post(f"{QUERY_MANAGER}/QueryData/ExecutionPlanningAggregate", 
                data    = json.dumps(pipeline, cls=CustomJSONEncoder), 
                headers = headers, 
                verify  = VERIFY_HTTPS
            )
            if res.status_code != 200: 
                raise Exception(f"Error getting execution planning {res.status_code} {res.content}")
            
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            
            total_docs      = content["data"]["total"]
            page_size       = content["data"]["size"]
            total_batchs    = (total_docs // page_size) + 1
            logger.info(f"Total documents to download {total_docs}, batch size {page_size}, total batchs {total_batchs}")
            if total_docs == 0: return False

            client = httpx.AsyncClient(headers=headers, verify=VERIFY_HTTPS, timeout=httpx.Timeout(60.0, connect=10.0, read=1200.0))
            tasks = []
            for page in range(1, total_batchs + 1):
                tasks.append(self.fetch_page_agg(client, ikey, pipeline, page, page_size))
            await asyncio.gather(*tasks)

            logger.info("All pages downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error to aggregate data in inputstream {e}", stack_info=True)
            return False


    def send_example(self, ikey:str, example:dict) -> dict:
        try:
            headers = { 
                "Authorization": f"A2G {self.token}", 
                "ikey": ikey,
                'Content-Type': 'application/json'
            }
            res = requests.post(f"{DATA_URL}/Data/Insert", 
                data=json.dumps(example, cls=CustomJSONEncoder),
                headers=headers, 
                verify=VERIFY_HTTPS
            )
            if res.status_code != 200: raise Exception(f"Error sending example {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return content["data"]
        except Exception as e:
            raise e
        

    async def insert_data(self, 
        ikey:str, 
        data:list[dict], 
        mode:INSERTION_MODE, 
        wait_response:bool,
        batch_idx:int,
        batch_size:int
    ) -> tuple[int, str]:
        """
        insert data into inputstream internal
        params:
            ikey: str
            data: list[dict]
            mode: INSERTION_MODE
            wait_response: bool
            i: int -> only for logging
            batch_size: int -> only for logging
        """
        try:
            async with SEM:
                timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                async with httpx.AsyncClient(verify=VERIFY_HTTPS, timeout=timeout) as client:

                    # TODO: revisar si se puede gzipper el contenido
                    headers = {
                        "Authorization": f"A2G {self.token}",
                        "ikey": ikey,
                        'Content-Type': 'application/json',
                        "Content-Encoding": "gzip"
                    }

                    if mode == INSERTION_MODE.REPLACE: 
                        headers["Replace"] = "true"
                        headers["Transaction"] = "false"

                    elif mode == INSERTION_MODE.INSERT_UNORDERED: 
                        headers["Replace"] = "false"
                        headers["Transaction"] = "false"

                    elif mode == INSERTION_MODE.TRANSACTION:
                        headers["Replace"] = "false"
                        headers["Transaction"] = "true"

                    if wait_response: headers["WaitResponse"] = "true"

                    # Envia un lote de datos al servidor
                    body = gzip.compress(json.dumps(data, cls=CustomJSONEncoder).encode(), compresslevel=7)
                    start = datetime.now()
                    logger.info(f"Inserting batch {batch_idx} into inputstream {ikey}...")
                    response:Response = await client.post(f"{DATA_URL}/Data/Insert", content = body, headers = headers)
                    if response.status_code != 200: 
                        raise Exception(f"Error to insert data in inputstream {response.status_code} {response.text}")
                    logger.info(f"Batch {batch_idx} received successfully, batch size: {batch_size}, elapsed time: {datetime.now() - start}")
                    return response.status_code, response.text
                
        except Exception as e:
            logger.error(f"Error to insert data in inputstream {e}", exc_info=True)
            raise e


    async def insert_data_external(self, ikey:str, table: str, data:list[dict], batch_idx:int, batch_size:int) -> None:
        """
        insert data into external inputstream using http2 and stream
        params:
            ikey: str
            table_name: str
            data: list[dict]
        """
        async with SEM:
            timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
            async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:

                # TODO: revisar si se puede gzipper el contenido
                headers = {
                    "Authorization": f"A2G {self.token}",
                    "ikey": ikey,
                    'Content-Type': 'text/plain'
                }

                # Envia un lote de datos al servidor
                my_body = { "list_data": data, "table_name": table }
                logger.info(f"Inserting batch {batch_idx} into inputstream {ikey}...")
                async with client.stream("POST",f"{QUERY_MANAGER}/QueryData/InsertDataExternal",
                    content = json.dumps(my_body, cls=CustomJSONEncoder), 
                    headers = headers
                ) as response:
                    if response.status_code != 200:
                        msg = ""
                        async for chunk in response.aiter_bytes():
                            if chunk:
                                msg += chunk.decode("utf-8")
                        raise Exception(f"{response.status_code} {msg}")
            logger.info(f"Batch {batch_idx} received successfully, batch size: {batch_size}")


    def convert_types(self, obj):
        try:
            if isinstance(obj, Decimal):
                return float(obj)  # O str(obj) si prefieres preservar precisión
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            elif isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')  # Convierte bytes a string
            # Agrega más conversiones aquí si es necesario
            return obj
        except Exception as e:
            raise(e)

    async def data_generator(self, data_source, batch_size, table_name):
        """
        Un generador asíncrono que envía datos en lotes como chunks.
        """
        batch = []
        for record in data_source:
            batch.append(record)
            if len(batch) == batch_size:                            
                payload = {
                    "list_data": [{key: self.convert_types(value) for key, value in row.items()} for row in batch],
                    "table_name": table_name,
                }
                yield msgpack.packb(payload) + b'>I'
                batch = []
        # Procesar los datos restantes si no alcanzaron el tamaño del batch
        if batch:                    
            payload = {
                "list_data": [{key: self.convert_types(value) for key, value in row.items()} for row in batch],
                "table_name": table_name,
            }
            yield msgpack.packb(payload) + b'>I'

    async def insert_data_big_external(self, ikey:str, table: str, data:list[dict]) -> None:
        """
        insert big data into external inputstream using http2 and stream
        params:
            ikey: str
            table_name: str
            data: list[dict]
        """

        batch_size = 50000
        try:
            timeout = httpx.Timeout(connect=10.0, read=600.0, write=600.0, pool=600.0)
            async with httpx.AsyncClient(http2=True, verify=VERIFY_HTTPS, timeout=timeout) as client:
                # TODO: revisar si se puede gzipper el contenido
                headers = {
                    "Authorization": f"A2G {self.token}",
                    "ikey": ikey,
                    'Content-Type': 'text/plain'
                }
                logger.info(f"Inserting data into inputstream {ikey}...")
                async with client.stream("POST",f"{QUERY_MANAGER}/QueryData/InsertDataBigExternal",
                    content = self.data_generator(data, batch_size=batch_size, table_name=table), 
                    headers = headers
                ) as response:                
                    if response.status_code == 200:
                        async for line in response.aiter_text():  # Procesar línea por línea
                            logger.info(f"Server response: {line}")
                    else:
                        logger.error(f"Failed to insert data: {response.status_code} - {response.text}")
        except asyncio.CancelledError as e:
            logger.info("La tarea fue cancelada.", e)
            raise
        except Exception as e:
            logger.info(f"Error general: {e}")     


    async def remove_documents(self, ikey: str, query: dict) -> int:
        try:
            logger.info("Removing data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey,
                'Content-Type': 'application/json'
            }

            if len(query) == 0: 
                raise Exception("Query is empty, please provide a valid query. If you desire to delete all documents, use the clear_inputstream method.")

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                response = await client.post(
                    f"{QUERY_MANAGER}/QueryData/RemoveDocuments",
                    data=json.dumps(query, cls=CustomJSONEncoder),
                    headers=headers,
                    timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                )

            if response.status_code != 200: 
                raise Exception(f"Error to remove data in inputstream {response.status_code} {response.content}")
            
            res_object = json.loads(response.text, cls=CustomJsonDecoder)
            if not res_object["success"]: 
                raise Exception(res_object["errorMessage"])

            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")

            return deleted_docs
        except Exception as e:
            raise e


    async def clear_inputstream(self, ikey:str) -> int:
        try:
            logger.info("Removing all data...")
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }

            async with httpx.AsyncClient(verify=VERIFY_HTTPS) as client:
                response = await client.post(
                    f"{QUERY_MANAGER}/QueryData/Clear",
                    headers=headers,
                    timeout = httpx.Timeout(60.0, connect=10.0, read=600.0)
                )

            if response.status_code != 200:
                raise Exception(f"Error to remove all data in inputstream {response.status_code} {response.content}")
            
            res_object = response.json(cls=CustomJsonDecoder)
            if not res_object["success"]: raise Exception(res_object["errorMessage"])
            
            content = res_object["data"]
            deleted_docs = content["docs_affected"]
            logger.info(f"Operation complete, total docs deleted: {deleted_docs}")
            return deleted_docs
        except Exception as e:
            logger.error(f"Error to clear inputstream {e}", exc_info=True)
            raise e

