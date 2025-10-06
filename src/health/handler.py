import json
import os
from datetime import datetime, timezone

def handler(event, context):
    now = datetime.now(timezone.utc).isoformat()
    region = os.getenv( "AWS_REGION", "eu-west-3")
    body = {
        "status": "ok",
        "service": "mini-api",
        "region": region,
        "time": now,
    }
    return {
        "statusCode": 200,
        "headers":{"Content-Type": "application/json"},
        "body": json.dumps(body),
    }