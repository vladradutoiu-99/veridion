from os import environ

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


OTEL_HOST = environ.get("OTEL_HOST", "http://otel:4318/v1/traces")

def initialize_tracer_with_instrumentation(
    service_name: str, 
):
    initialize_tracer_without_instrumentation(service_name)

    RequestsInstrumentor().instrument()
    CeleryInstrumentor().instrument()


def initialize_tracer_without_instrumentation(service_name: str):
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({SERVICE_NAME: service_name})
    ))

    otlp_exporter = OTLPSpanExporter(endpoint=OTEL_HOST)
    span_processor = SimpleSpanProcessor(otlp_exporter)
    
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    
    tracer = trace.get_tracer(__name__)

    return tracer