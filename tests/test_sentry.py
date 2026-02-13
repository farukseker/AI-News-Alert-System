import sentry_sdk
from sentry_sdk.transport import HttpTransport

sentry_sdk.init(
    dsn=,
    traces_sample_rate=1.0,
    debug=True,  # detayli log
)

sentry_sdk.capture_message("Test message from Python")
z = 1 / 0
sentry_sdk.flush(timeout=10)
print("Done")