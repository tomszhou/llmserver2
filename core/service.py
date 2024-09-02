
import time
import torch

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from config.logger import logger
from core.model import LlmChat2Model,LlmChatModel


def success_response(id, created, used_time, chat_answer, request_id):
    headers = {"X-BC-Request-Id" : request_id}
    content = {
        "id": id,
        "created": created,
        "used_time": used_time,
        "errcode": 0,
        "errmsg": "success",
        "message": {
            "role": "assistant",
            "content": chat_answer,
        }
    }
    return JSONResponse(status_code=200, headers=headers, content=content)

def error_response(id, created, used_time, request_id):
    headers = {"X-BC-Request-Id" : request_id}
    content = {
        "id": id,
        "created": str(created),
        "finish_reason": "error",
        "used_time": str(used_time),
        "errcode": 500,
        "errmsg": "Internal Server Error",
    }
    return JSONResponse(status_code=500, headers=headers ,content=content)


async def chat_completions(chat: LlmChat2Model, request: Request):
    model = request.app.state.model
    tokenizer = request.app.state.tokenizer
    request_id = request.headers.get("X-BC-Request-Id", "")
    start_time = time.time()
    created = int(start_time)
    id = await request.app.sequence_id(created)
    logger.info(f"messages: {chat.messages}")
    chat_messages = []
    for message in chat.messages:
        chat_messages.append({"role" : message.role, "content" :  message.content})
    try:
        chat_answer = model.chat(tokenizer, chat_messages)
        used_time = round(time.time() - start_time, 2)
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        return success_response(id, created, used_time, chat_answer, request_id)
    except Exception as e:
        logger.error(f"model exception: {str(e)}")
        used_time = time.time() - start_time
        return error_response(id, created, used_time, request_id)


# 不实现 sse 协议
async def chat_completions_stream(chat: LlmChat2Model, request : Request):
    model = request.app.state.model
    tokenizer = request.app.state.tokenizer
    request_id = request.headers.get("X-BC-Request-Id", "")
    start_time = time.time()
    created = int(start_time)
    id = await request.app.sequence_id(created)
    media_type = "text/event-stream"
    logger.info(f"messages: {chat.messages}")
    chat_messages = []
    for message in chat.messages:
        chat_messages.append({"role" : message.role, "content" :  message.content})
    try:
        streamer = model.chat(tokenizer, chat_messages, stream=True)
    except Exception as e:
        logger.error(f"model exception: {str(e)}")
        used_time = time.time() - start_time
        return error_response(id, created, used_time, request_id)
    
    async def stream_response():
        position = 0
        for chat_answer in streamer:
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            yield chat_answer[position:]
            position = len(chat_answer)
    
    return StreamingResponse(stream_response(), media_type=media_type)


async def llmchat(chat: LlmChatModel, request: Request):
    model = request.app.state.model
    tokenizer = request.app.state.tokenizer
    request_id = request.headers.get("X-BC-Request-Id", "")
    start_time = time.time()
    created = int(start_time)
    id = await request.app.sequence_id(created)

    logger.info(f"messages: {chat.messages}")
    
    chat_messages = []
    for message in chat.messages:
        chat_messages.append({"role" : message.role, "content" :  message.content})

    try:
        chat_answer = model.chat(tokenizer, chat_messages)
        used_time = round(time.time() - start_time, 2)
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        return success_response(id, created, used_time, chat_answer, request_id)
    except Exception as e:
        logger.error(f"model exception: {str(e)}")
        used_time = time.time() - start_time
        return error_response(id, created, used_time, request_id)
    
async def llmchat_stream(chat: LlmChatModel, request: Request):
    model = request.app.state.model
    tokenizer = request.app.state.tokenizer
    request_id = request.headers.get("X-BC-Request-Id", "")
    start_time = time.time()
    created = int(start_time)
    id = await request.app.sequence_id(created)

    logger.info(f"messages: {chat.messages}")

    chat_messages = []

    for message in chat.messages:
        chat_messages.append({"role" : message.role, "content" :  message.content})

    try:
        streamer = model.chat(tokenizer, chat_messages, stream=True)
    except Exception as e:
        logger.error(f"model exception: {str(e)}")
        used_time = time.time() - start_time
        return error_response(id, created, used_time, request_id)
    
    media_type = "text/event-stream"
    
    async def stream_response():
        position = 0
        for chat_answer in streamer:
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            yield chat_answer[position:]
            position = len(chat_answer)
            
    return StreamingResponse(stream_response(), media_type=media_type)

async def health_check():
    health = {
        "status" : "ok",
    }

    return JSONResponse(
        status_code = 200,
        content = health
    )

def initialize_router(app: FastAPI):
    app.add_api_route("/v1/health/check", health_check, methods=["GET"])
    app.add_api_route("/v1/chat/completions", chat_completions, methods=["POST"])
    app.add_api_route("/v1/chat/completions/stream", chat_completions_stream, methods=["POST"])
    app.add_api_route("/v1/chat/llmchat", llmchat, methods=["POST"])
    app.add_api_route("/v1/chat/llmchat/stream", llmchat_stream, methods=["POST"])
