import json
import os
import base64
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
BUCKET = os.getenv("UPLOADS_BUCKET")
PREFIX = os.getenv("UPLOADS_PREFIX", "uploads/")

def handler(event, context):
    # Attend: JSON {"filename": "note-123.txt", "content": "hello world"}
    try:
        if "body" not in event:
            return _resp(400, {"error": "Missing body"})

        # API GW peut livrer body en string; si c'est du base64 via certains mappings, adapter ici.
        body = event["body"]
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")

        data = json.loads(body)
        filename = data.get("filename")
        content  = data.get("content")

        if not filename or not content:
            return _resp(400, {"error": "filename and content are required"})

        # Petite normalisation de nom (optionnel, simple)
        if "/" in filename:
            return _resp(400, {"error": "filename must not contain '/'"})

        key = f"{PREFIX}{filename}"

        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType="text/plain; charset=utf-8"
        )

        return _resp(201, {
            "message": "uploaded",
            "key": key,
            "bucket": BUCKET,
            "time": datetime.now(timezone.utc).isoformat()
        })

    except json.JSONDecodeError:
        return _resp(400, {"error": "invalid JSON"})
    except Exception as e:
        return _resp(500, {"error": str(e)})

def _resp(status, obj):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(obj),
    }