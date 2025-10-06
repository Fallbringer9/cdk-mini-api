from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_logs as logs,
    aws_s3 as s3
)
from constructs import Construct


class CdkMiniApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda: GET /health
        health_fn = _lambda.Function(
            self, "HealthFunction",
            function_name="mini-api-health",
            description="Returns service health status",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",                         # fichier .py + fonction
            code=_lambda.Code.from_asset("src/health"),        # dossier packagé
            timeout=Duration.seconds(3),
            memory_size=128,
            environment={},
            log_retention=logs.RetentionDays.ONE_WEEK,          # coûts/logs maîtrisés
        )

        # API Gateway
        api = apigw.RestApi(
            self, "MiniApi",
            rest_api_name="mini-api",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                logging_level=apigw.MethodLoggingLevel.INFO,
                data_trace_enabled=False,
                metrics_enabled=True,                          # métriques CloudWatch
            ),
            cloud_watch_role=True,
        )

        # Route: /health (GET) -> Lambda health_fn
        health_integration = apigw.LambdaIntegration(health_fn)
        api.root.add_resource("health").add_method("GET", health_integration)

        # Bucket S3 privé pour les uploads
        bucket = s3.Bucket(
            self, "UploadsBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        )

        # Lambda: POST /upload
        upload_fn = _lambda.Function(
            self, "UploadFunction",
            function_name="mini-api-upload",
            description="Stores text content into S3 under uploads/",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset("src/upload"),
            timeout=Duration.seconds(6),
            memory_size=128,
            environment={
                "UPLOADS_BUCKET": bucket.bucket_name,
                "UPLOADS_PREFIX": "uploads/",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Route: /upload (POST) -> Lambda upload_fn
        upload_integration = apigw.LambdaIntegration(upload_fn)
        api.root.add_resource("upload").add_method("POST", upload_integration)

        # IAM minimal: autoriser uniquement PutObject sur le préfixe uploads/*
        bucket.grant_put(upload_fn, "uploads/*")