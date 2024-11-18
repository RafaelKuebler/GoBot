#!/usr/bin/env python3

import os

import aws_cdk as cdk

from infrastructure.stacks.gobot_stack import GoBotStack

app = cdk.App()
GoBotStack(
    app,
    "GoBotStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
