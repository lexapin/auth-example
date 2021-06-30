import aiofiles
import aiohttp
import asyncio
import json
import uuid
import time

from asyncio.exceptions import TimeoutError
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel


class TimeProfiler:
    def __enter__(self):
        self.time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"--- function time is {time.time()-self.time} ---")


sources = [
    {
        "name": 1,
        "type": "file",
        "files": ["./data/sample_1.json", "./data/sample_30.json"]
    },
    {
        "name": 2,
        "type": "file",
        "files": ["./data/sample_2.json", "./data/sample_4.json"]
    },
    {
        "name": 3,
        "type": "http",
        "files": ["./data/sample_3.json", "./data/sample_6.json"]
    },
]

app = FastAPI()

TASK_MANAGER = {}


async def get_data_from_file(file_path):
    async with aiofiles.open(file_path, mode='r') as f:
        data = await f.read()
    return json.loads(data)


async def file_source(file_path):
    await asyncio.sleep(1)
    result = []
    try:
        result.extend(await get_data_from_file(file_path))
    except BaseException:
        pass
    print("file_source complete read files", file_path)
    return result


async def http_source(file_path):
    await asyncio.sleep(1)
    result = []
    url = "http://localhost:8000/get/data/from/file"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json={"path": file_path}) as response:
                response.raise_for_status()
                if response.content_type == 'application/json':
                    result.extend(await response.json())
    except TimeoutError:
        pass
    except BaseException:
        pass
    print("http_source complete read files", file_path)
    return result


async def get_data_task(task_id):
    with TimeProfiler():
        TASK_MANAGER[task_id].update({
            "status": "in_progress"
        })
        tasks = []
        result = []
        for source in sources:
            get_data_function = None
            if source["type"] == "file":
                get_data_function = file_source
            elif source["type"] == "http":
                get_data_function = http_source
            if get_data_function is None:
                continue
            for file_path in source["files"]:
                task = asyncio.create_task(get_data_function(file_path))
                tasks.append(task)
        await asyncio.sleep(2)
        for task in tasks:
            if task.done():
                result.extend(task.result())
            else:
                task.cancel()
        result.sort(key=lambda item: item["id"])
        TASK_MANAGER[task_id].update({
            "result": result,
            "status": "complete"
        })


@app.post("/tasks")
async def create_task(background_tasks: BackgroundTasks):
    task_id = uuid.uuid4()
    TASK_MANAGER[task_id] = {
        "result": None,
        "status": "created",
        "id": str(task_id)
    }
    background_tasks.add_task(get_data_task, task_id)
    return TASK_MANAGER[task_id]


@app.get("/tasks/{task_id}")
async def get_task_result(task_id: uuid.UUID):
    if task_id in TASK_MANAGER:
        return TASK_MANAGER[task_id]
    raise HTTPException(404)


async def waitable_object(function_to_wait, data, time_to_wait=2.0):
    try:
        result = await asyncio.wait_for(function_to_wait(data), time_to_wait)
    except TimeoutError:
        print(">>>>>>>>>>>TIMEOUT")
        result = []
    finally:
        return result


@app.post("/tasks/arni")
async def get_data_in_request():
    result = []
    with TimeProfiler():
        coroutines = []
        for source in sources:
            get_data_function = None
            if source["type"] == "file":
                get_data_function = file_source
            elif source["type"] == "http":
                get_data_function = http_source
            if get_data_function is None:
                continue
            for file_path in source["files"]:
                coroutines.append(waitable_object(get_data_function, file_path))
        grouped_result = await asyncio.gather(*coroutines)
        for res in grouped_result:
            result.extend(res)
        result.sort(key=lambda item: item["id"])
    return result


class PathModel(BaseModel):
    path: str


@app.get("/get/data/from/file")
async def data_from_file(data: PathModel):
    await asyncio.sleep(5)
    return await get_data_from_file(data.path)
