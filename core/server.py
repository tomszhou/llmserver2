# -*- coding: utf-8 -*-
import time
import torch
import aioredis
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from transformers.generation.utils import GenerationConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from config.config import ServerConfig
from config.logger import logger

class LlmFastAPI(FastAPI):
    config = {}
    device : str = ""
    node : str = ""

    def __init__(self, *args, **kwargs) -> None:
        config = kwargs.pop("config", None)
        super().__init__(*args, **kwargs)
        self.config = config if config is not None else ServerConfig()
        self.node = self.config.get("NODE_ID", "server")

    def max_workers(self):
        _devices = self.config.get("GPU_DEVICE_MAP", [])
        logger.info(f"_devices = {_devices}, {len(_devices)}")
        return len(_devices)
    
    async def init_redis(self):
        redis : aioredis.Redis = None
        redis_url = self.config.get("REDIS_URL", None)
        redis = aioredis.Redis.from_url(redis_url, decode_responses=True)
        self.state.redis = redis

    async def try_acquire_lock(self, lock_key: str, timeout=5):
        if await self.state.redis.setnx(lock_key, 1):
            await self.state.redis.expire(lock_key, timeout)
            return True
        return False
    
    async def release_lock(self, lock_key : str):
        r = self.state.redis
        await r.delete(lock_key)

    async def allocate_gpu(self):
        _device_list = self.config.get("GPU_DEVICE_MAP",[])
        for device in _device_list:
            lock_key = f"GPU:LOCK:{device}"
            if await self.try_acquire_lock(lock_key):
                self.device = device
                return device
        return None

    async def release_gpu(self):
        lock_key = f"GPU:LOCK:{self.device}"
        await self.release_lock(lock_key)


    async def load_model(self):
        device = await self.allocate_gpu()
        if device is None:
            raise ValueError(f"Can't attach GPU device")

        model_name = self.config.get("MODEL_NAME", "")
        if model_name is None:
            raise ValueError(f"You are not set model name")
        
        model_dir = self.config.get(model_name.upper() + "_MODEL_PATH", "")
        if model_dir is None:
            raise ValueError(f"You are not set {model_name.upper() + '_MODEL_PATH'} environment variable")
        
        cache_dir = self.config.get(model_name.upper() + "_MODEL_CACHE_PATH", "")
        if cache_dir is None:
            raise ValueError(f"You are not set {model_name.upper() + '_MODEL_CACHE_PATH'} environment variable")

        tokenizer = AutoTokenizer.from_pretrained(
                            model_dir, 
                            cache_dir=cache_dir,
                            se_fast = False,
                            trust_remote_code = True
                        )
        
        model = AutoModelForCausalLM.from_pretrained(
                            model_dir, 
                            cache_dir=cache_dir,
                            device_map = device, 
                            torch_dtype = torch.float32,
                            trust_remote_code = True
                        )
        
        model.generation_config = GenerationConfig.from_pretrained(model_dir)

        self.state.tokenizer = tokenizer
        self.state.model = model

    async def init_sequence(self):
        self.state.sequence_number = 0
        self.state.lock = asyncio.Lock()

    async def sequence_id(self, created: int) -> str:
        async with self.state.lock:
            self.state.sequence_number = (self.state.sequence_number + 1) % 1000000
            formatted_id = f"{self.node}:{self.device}:{created:010d}:{self.state.sequence_number:06d}"
            return formatted_id

def initialize_middleware(app: FastAPI):
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts = ["172.16.1.80", "172.16.1.70","172.16.1.120","127.0.0.1","localhost"]
    )

# 异步上下文管理器加载和卸载模型
@asynccontextmanager
async def lifespan(app : FastAPI):
    start_time = time.time()
    logger.info("initialize redis")
    await app.init_redis()
    logger.info("initialize model")
    await app.load_model()
    logger.info(f"initialize resource used {time.time() - start_time:.2f} seconds")
    await app.init_sequence()
    yield
    logger.info(f"ready shutdown, clear cuda")
    torch.cuda.empty_cache()
    logger.info(f"ready shutdown, close model")
    app.state.model = None 
    logger.info(f"ready shutdown, close redis")
    await app.state.redis.close()
    logger.info(f"shutdown.")
