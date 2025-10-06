import os
import aws_cdk as cdk

from cdk_mini_api.cdk_mini_api_stack import CdkMiniApiStack

app = cdk.App()

# Utilise le compte/region fournis par l'environnement (profils AWS) ou force eu-west-3 par défaut
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION") or "eu-west-3",
)

CdkMiniApiStack(app, "CdkMiniApiStack", env=env)

app.synth()
