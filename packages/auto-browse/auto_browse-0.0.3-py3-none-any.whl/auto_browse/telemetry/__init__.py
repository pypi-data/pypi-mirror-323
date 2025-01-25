import os
from datetime import datetime
import platform
from posthog import Posthog

posthog = Posthog(
    project_api_key='phc_4pwxr91oy6WYPfaD13ClVreSbT7F7ClJcAEyBpTQCOl',
    host='https://us.i.posthog.com'
)

def log_event(event_name: str, properties: dict):
    if os.getenv('AUTOBROWSE_ANONYMIZED_TELEMETRY', 'true').lower() != 'false':
        properties.update({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'os': platform.system(),
            'os_version': platform.version()
        })
        posthog.capture(event_name, properties)
