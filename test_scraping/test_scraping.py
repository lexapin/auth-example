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


async def file_source(file_paths):
    await asyncio.sleep(1)
    result = []
    for file_path in file_paths:
        try:
            result.extend(await get_data_from_file(file_path))
        except BaseException:
            pass
    print("file_source complete read files", file_paths)
    return result


async def http_source(file_paths):
    await asyncio.sleep(1)
    result = []
    url = "http://localhost:8000/get/data/from/file"
    for file_path in file_paths:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, json={"path": file_path}) as response:
                    response.raise_for_status()
                    if response.content_type == 'application/json':
                        result.extend(await response.json())
        except BaseException:
            pass
    print("file_source complete read files", file_paths)
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
            try:
                task_result = await asyncio.wait_for(get_data_function(source["files"]), 2)
                if task_result:
                    result.extend(task_result)
            except TimeoutError:
                pass
        result.sort(key=lambda item: item["id"])
        TASK_MANAGER[task_id].update({
            "result": result,
            "status": "complete"
        })


# async def get_data_task(task_id):
#     with TimeProfiler():
#         TASK_MANAGER[task_id].update({
#             "status": "in_progress"
#         })
#         tasks = []
#         result = []
#         for source in sources:
#             get_data_function = None
#             if source["type"] == "file":
#                 get_data_function = file_source
#             elif source["type"] == "http":
#                 get_data_function = http_source
#             if get_data_function is None:
#                 continue
#             task = asyncio.create_task(get_data_function(source["files"]))
#             tasks.append(task)
#         for task in tasks:
#             try:
#                 task_result = await asyncio.wait_for(task, 2)
#                 if task_result:
#                     result.extend(task_result)
#             except TimeoutError:
#                 pass
#         result.sort(key=lambda item: item["id"])
#         TASK_MANAGER[task_id].update({
#             "result": result,
#             "status": "complete"
#         })


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


class PathModel(BaseModel):
    path: str


@app.get("/get/data/from/file")
async def data_from_file(data: PathModel):
    return await get_data_from_file(data.path)
