# -*- coding: utf-8 -*-
import os
import dotenv
from typing import Any

MAIN_CONFIG_NAME = "llmserver2_cfg"

def load_environ():
    env_file = os.environ.get(MAIN_CONFIG_NAME.upper(), None)
    dotenv.load_dotenv(dotenv_path=env_file)

try:
    load_environ()
except Exception :
    raise ValueError("Must set config-file('LLMSERVER2-CFG') Environment variable")

#  .ven
DEFAULTS = {
    "NODE_ID" : "aiserver",
    "REDIS_URL" : "redis://172.16.1.70:6379/1",
    "MODEL_NAME" : "baichuan",
    "BAICHUAN_MODEL_CACHE_PATH" : "/home/baichuan/.cache/huggingface/modules/transformers_modules",
    "BAICHUAN_MODEL_PATH" : "/model_data/BaiChuan2/13B-Chat",
    "LOG_PATH" : "/home/baichuan/logs",
    "GPU_DEVICE_MAP" : ["cuda:0","cuda:1"]
}


class ServerConfig(dict):
    def __init__(self) -> None:
        super().__init__()
        for key, default_value in DEFAULTS.items():
            env_value = os.environ.get(key, None)
            if env_value is None:
                value_to_set = default_value
            else:
                value_to_set = self._convert_value(env_value, default_value)
            self[key] = value_to_set
    
    def _convert_value(self, value, default):
        if isinstance(default, bool):
            return value.lower() in ('true', '1')
        elif isinstance(default, int):
            return int(value)
        elif isinstance(default, list):
            return value.split(',')
        return value
    
    def __getattr__(self, attr: Any):
        try:
            return self[attr]
        except KeyError as ke:
            raise AttributeError(f"Config has no '{ke.args[0]}'")
        
    def __setattr__(self, key, value):
        self[key] = value

    def as_dict(self):
        return dict(self)

