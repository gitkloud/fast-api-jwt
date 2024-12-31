from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
import time
import uvicorn
from app.appconfig import app_success_msg
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server, generate_latest, REGISTRY

SECRET_KEY = "your_secret_key"

app = FastAPI()

# Set up OpenTelemetry
resource = Resource(attributes={
    "service.name": "my-fastapi-app"
})
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)

# Set up OpenTelemetry Metrics
prometheus_exporter = PrometheusMetricReader()
meter_provider = MeterProvider(resource=resource)
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
meter_provider._all_metric_readers.add(metric_reader)

# Create a meter
meter = meter_provider.get_meter("my-fastapi-app")

# Create a counter
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

@app.middleware("http")
async def add_metrics(request, call_next):
    response = await call_next(request)
    request_counter.add(1, {"method": request.method, "endpoint": request.url.path})
    return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict):
    to_encode = data.copy()
    expire = time.time() + 30
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "Password@1":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def read_secure_data(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return app_success_msg()

@app.get("/metrics")
async def metrics(request: Request):
    return PlainTextResponse(generate_latest(REGISTRY))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
