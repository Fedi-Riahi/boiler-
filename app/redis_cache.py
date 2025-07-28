import redis
import os
redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(
    host=redis_host,
    port=6379,
    db=0,
    decode_responses=True
  )
