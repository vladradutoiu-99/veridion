from os import environ
from typing import Any, Callable, Dict, List, Tuple, Type, Optional
from fastapi import  APIRouter, FastAPI

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace


from app.api.middleware import LoggingMiddleware

OTEL_HOST = environ.get("OTEL_HOST", "http://otel:4318/v1/traces")

class FastAPIAppBuilder:
    def __init__(self):
        self.middlewares: List[Tuple[Any, Dict[str, Any]]] = []
        self.startup_fn: Optional[Callable] = None
        self.has_celery_publisher = False
        self.tracer = None

    def with_middleware(self, middleware: type, **options: Any):
        self.middlewares.append((middleware, options))
        return self
    
    def with_startup_function(self, startup_fn: Callable):
        self.startup_fn = startup_fn
        return self


    def with_celery_publisher(self):
        self.has_celery_publisher = True

        return self

    def build(self):
        lifespan_fn = None


        if self.has_celery_publisher:
            trace.set_tracer_provider(TracerProvider(
                resource=Resource.create({SERVICE_NAME: "server_app"})
            ))
            otlp_exporter = OTLPSpanExporter(endpoint=OTEL_HOST)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            CeleryInstrumentor().instrument()

        app = FastAPI(lifespan=lifespan_fn)

        for middleware_with_options in self.middlewares:
            middleware, options = middleware_with_options
            app.add_middleware(middleware, **options)

        if self.tracer:
            FastAPIInstrumentor.instrument_app(app)

        return app


api_base_builder = (
    FastAPIAppBuilder()
    .with_middleware(LoggingMiddleware)
)
