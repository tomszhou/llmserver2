# -*- coding: utf-8 -*-

from fastapi import (
    FastAPI, 
    Request, 
    HTTPException
)

from pydantic import  ValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.logger import logger

async def http_exception_handler(request: Request, exception: HTTPException):
    import traceback
    tb = traceback.TracebackException.from_exception(exception)
    logger.error(f"{request.url.path}: {''.join(tb.format())}")
    return JSONResponse(
        status_code = exception.status_code,
        content={"errcode": exception.status_code, "errmsg": exception.detail}
    )

async def starlette_exception_handler(request: Request, exception: StarletteHTTPException):
    import traceback
    tb = traceback.TracebackException.from_exception(exception)
    logger.error(f"{request.url.path}: {''.join(tb.format())}")
    return JSONResponse(
        status_code = exception.status_code,
        content = {"errcode": exception.status_code, "errmsg": f"{exception.detail}"}
    )

async def validation_exception_handler(request: Request, exception: ValidationError):
    errors = exception.errors()
    missing_fields = [error['loc'][0] for error in errors if error['type'] == 'value_error.missing']
    logger.error(f"{request.url.path}: Missing fields: {missing_fields}")
    logger.error(f"{errors}")
    return JSONResponse(
        status_code = 422,
        content = {"errcode": 422, "errmsg": f"Missing fields: {missing_fields}"}
    )

async def other_exception_handler(request: Request, exception: Exception):
    import traceback
    tb = traceback.TracebackException.from_exception(exception)
    logger.error(f"{request.url.path}: {''.join(tb.format())}")
    return JSONResponse(
        status_code = 500,
        content = {"errcode": 500, "errmsg": "Internal Server Error, 服务器内部错误"}
    )

async def reqeust_Validation_exception_handler(request: Request, exception: RequestValidationError):
    errors = exception.errors()
    missing_fields = [error['loc'][0] for error in errors if error['type'] == 'value_error.missing']
    logger.error(f"{request.url.path}: Missing fields: {missing_fields}")
    logger.error(f"{exception.body}")
    logger.error(f"{errors}")
    import traceback
    tb = traceback.TracebackException.from_exception(exception)
    logger.error(f"{request.url.path}: {''.join(tb.format())}")
    return JSONResponse(
        status_code = 500,
        content = {"errcode": 500, "errmsg": "Internal Server Error, 服务器内部错误"}
    )


def initialize_error_handler(app: FastAPI):
    app.add_exception_handler(
        HTTPException, 
        http_exception_handler
    )
    app.add_exception_handler(
        StarletteHTTPException, 
        starlette_exception_handler
    )
    app.add_exception_handler(
        ValidationError, 
        validation_exception_handler
    )

    app.add_exception_handler(
        RequestValidationError, 
        reqeust_Validation_exception_handler
    )

    app.add_exception_handler(
        Exception, 
        other_exception_handler
    )
