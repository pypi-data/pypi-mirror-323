#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : videos
# @Time         : 2025/1/15 15:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from meutils.schemas.task_types import TaskResponse
from meutils.schemas.video_types import FalVideoRequest

from meutils.schemas.fal_types import FEISHU_URL
from meutils.config_utils.lark_utils import get_next_token_for_polling

from fal_client import AsyncClient


# 平台/模型/版本
def model_mapper(model: str):
    return f"fal-ai/{model.removeprefix('fal-ai/')}"


async def create_task(request: FalVideoRequest, token: Optional[str] = None):
    """https://fal.ai/models/fal-ai/latentsync/api#queue-submit

    todo: 判别任务
    """
    token = token or await get_next_token_for_polling(feishu_url=FEISHU_URL)
    logger.debug(request)

    application = f"fal-ai/{request.model}"

    client = AsyncClient(key=token)
    response = await client.submit(
        application=application,
        arguments=request.model_dump(exclude_none=True, exclude={"model"})
    )
    # AsyncRequestHandle(request_id='0b7ab6b8-c7dc-4f17-a655-4ee56dd0f864')

    return TaskResponse(task_id=f"{request.model}::{response.request_id}", system_fingerprint=token)


@alru_cache(ttl=5)
async def get_task(task_id: str, token: Optional[str] = None):
    model, request_id = task_id.rsplit('::', 1)
    application = f"fal-ai/{model}"

    client = AsyncClient(key=token)
    response = await client.status(application, request_id, with_logs=False)
    logger.debug(response)

    # response = await client.result(application, request_id)
    # client.AsyncRequestHandle(request_id='0b7ab6b8-c7dc-4f17-a655-4ee56dd0f864')
    return response




if __name__ == '__main__':
    model = "latentsync"
    model = "sync-lipsync"
    audio_url = "https://oss.ffire.cc/files/lipsync.mp3"
    video_url = "https://oss.ffire.cc/files/lipsync.mp4"
    request = FalVideoRequest(
        model=model,
        audio_url=audio_url,
        video_url=video_url
    )

    r = arun(create_task(request))


    task_id = r.task_id
    arun(get_task(task_id, r.system_fingerprint))

    # task_id="latentsync::d4133f01-0f5b-4213-abe4-d14abdb57e3f"
    # token = "3f712efa-a692-4e7f-9409-e6c505bab4e2:151a0b6093312cc8f66fc52b7c4c92a8"

    # r = arun(get_task(task_id, token))
