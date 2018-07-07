# -*- encoding: UTF-8 -*-
import os
import redis

from stickers import STICKERS_TO_COUNT

GROUP_ID = os.environ['THE_LINE_GROUP_ID']
redis_client = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT'])
)

def conclude_stats():
    hash_key = 'GROUP_%s' % GROUP_ID
    previous_hash_key = 'GROUP_%s_PREVIOUS' % GROUP_ID
    redis_client.rename(hash_key, previous_hash_key)

if __name__ == "__main__":
    conclude_stats()
