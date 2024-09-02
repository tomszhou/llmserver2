import logging,logging.config

from config.config import ServerConfig
from config.logger import initialize_logging_config
from core.handler import initialize_error_handler
from core.server import LlmFastAPI, lifespan, initialize_middleware
from core.service import initialize_router

def initialize_server():
    cfg = ServerConfig()
    log_config = initialize_logging_config(cfg.get("LOG_PATH"))
    logging.config.dictConfig(log_config)

    app = LlmFastAPI(lifespan=lifespan, config=cfg)
    initialize_error_handler(app)
    initialize_middleware(app)
    initialize_router(app)
    return app, log_config

app, log_config = initialize_server()


if __name__ == "__main__":
    import uvicorn
    uvicorn_config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=9002,
        log_level="info",
        log_config=log_config,
        workers = app.max_workers()
    )
    print(f"workers = {app.max_workers()}")
    server = uvicorn.Server(uvicorn_config)
    server.run()




