#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : acache
# @Time         : 2025/1/14 09:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *

from aiocache import cached, Cache, RedisCache
from aiocache import multi_cached

# @multi_cached(ttl=60, caches=[Cache.MEMORY, Cache.MEMORY])
# async def complex_function(user_id, **kwargs):
#     logger.debug(user_id)
#     return False


# Cache.MEMORY

# Cache.REDIS
# mcache = cached(ttl=60, cache=Cache.REDIS)(cached)


rcache = Cache.from_url("redis://:chatfirechatfire@110.42.51.201:6379/11")
print(rcache)


# @cached(ttl=60)
@cached(ttl=15, cache=rcache)
async def complex_function(user_id, **kwargs):
    logger.debug(user_id)
    return False


class A(BaseModel):
    a: Any = 1


if __name__ == '__main__':
    arun(complex_function(A(a={})))
