import phoenix
from phoenix.otel import register
from opentelemetry.trace import Status, StatusCode

phoenix.launch_app(use_temp_dir=False)
tracer_provider_phoenix=register(project_name='abc', endpoint="http://127.0.0.1:6006/v1/traces")
tracer=tracer_provider_phoenix.get_tracer(__name__)
def test_print(abc):
    with tracer.start_as_current_span('test', openinference_span_kind="unknown") as span:
        span.add_event('start printing')
        span.set_input(abc)
        span.set_status(Status(StatusCode.OK))
test_print('xyz')
# input("abc")
