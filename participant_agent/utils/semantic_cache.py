import os

from dotenv import load_dotenv
from redisvl.extensions.llmcache import SemanticCache

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://host.docker.internal:6379/0")

# Semantic cache
hunting_example = "There's a deer. You're starving. You know what you have to do..."

# TODO: implement semantic cache
semantic_cache = None

# TODO store appropriate values in cache
# semantic_cache.store()
