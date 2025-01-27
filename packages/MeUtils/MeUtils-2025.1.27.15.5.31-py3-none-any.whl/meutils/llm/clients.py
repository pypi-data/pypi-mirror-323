#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat
# @Time         : 2024/8/19 14:23
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 
from openai import Client, AsyncClient, AsyncStream, APIStatusError

from meutils.pipe import *

OpenAI = lru_cache(Client)
AsyncOpenAI = lru_cache(AsyncClient)

moonshot_client = AsyncOpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url=os.getenv("MOONSHOT_BASE_URL")
)
zhipuai_client = AsyncOpenAI(
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPUAI_BASE_URL")
)

if __name__ == '__main__':
    from meutils.pipe import *

    # OpenAI().chat.completions.create(messages=[{"role": "user", "content": "hi"}], model='glm-4-flash')

    # arun(zhipuai_client.chat.completions.create(messages=[{"role": "user", "content": "hi"}], model='glm-4-flash'))

    # web-search-pro

    r = arun(zhipuai_client.chat.completions.create(
        messages=[{"role": "user", "content": "中国队奥运会拿了多少奖牌"}],
        model='web-search-pro')
    )

    r.model_dump_json()

