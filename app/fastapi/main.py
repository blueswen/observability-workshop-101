import logging
import os
import random
import time

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from utils import PrometheusMiddleware, metrics, setting_otlp

APP_NAME = os.environ.get("APP_NAME", "app")
EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "http://tempo:4317")

TARGET_ONE_SVC = os.environ.get("TARGET_ONE_SVC", "localhost:8000")
TARGET_TWO_SVC = os.environ.get("TARGET_TWO_SVC", "localhost:8000")

HTTPXClientInstrumentor().instrument()

app = FastAPI()

# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
app.add_route("/metrics", metrics)

# Setting OpenTelemetry exporter
setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)


class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@app.get("/")
async def read_root(request: Request):
    logging.info(f"Request headers: {request.headers}")
    logging.error("Hello World")
    logging.debug("Debugging log")
    logging.info("Info log")
    logging.warning("Hey, This is a warning!")
    logging.error("Oops! We have an Error. OK")
    return {"Hello": "World"}


@app.get("/io_task")
async def io_task():
    time.sleep(1)
    logging.error("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
    for i in range(1000):
        n = i * i * i
    logging.error("cpu task")
    return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
    response.status_code = random.choice([200, 200, 300, 400, 500])
    logging.error("random status")
    return {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
    time.sleep(random.randint(0, 5))
    logging.error("random sleep")
    return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
    logging.error("got error!!!!")
    raise ValueError("value error")


@app.get("/chain")
async def chain(response: Response):
    logging.info("Chain Start")
    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_ONE_SVC}/io_task",
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_SVC}/cpu_task",
        )
    logging.info("Chain End")
    return {"path": "/chain"}


@app.get("/random_fail")
async def random_fail(response: Response):
    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_ONE_SVC}/io_task",
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_SVC}/cpu_task",
        )
    if random.randint(0, 10) <= 2:
        async with httpx.AsyncClient() as client:
            await client.get(
                "http://localhost:8000/error_test",
            )
    return {"path": "/random_fail"}


if __name__ == "__main__":
    # update uvicorn access logger format
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT, log_config=log_config)
