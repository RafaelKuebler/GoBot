import os

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from constructs import Construct
from dotenv import load_dotenv


class GoBotStack(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        load_dotenv()

        gobot_lambda = _lambda.DockerImageFunction(
            self,
            id="GoBotDockerLambda",
            function_name="GoBotLambda",
            code=_lambda.DockerImageCode.from_image_asset(directory=".."),
            environment={
                "TOKEN": os.environ["TOKEN"],
                # "DATABASE_URL": "postgresql://gobot:gobot@localhost:5432",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        dynamodb_table = dynamodb.Table(
            self,
            "GobotGamesDynamoDBTable",
            table_name="gobot_games",
            partition_key=dynamodb.Attribute(
                name="chat_id",
                type=dynamodb.AttributeType.NUMBER,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )
        dynamodb_table.grant_read_write_data(gobot_lambda)
        gobot_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan",
                    "dynamodb:Query",
                ],
                resources=[dynamodb_table.table_arn],
                # arn:aws:dynamodb:eu-west-1:048378150643:table/gobot_games
                # arn:aws:dynamodb:eu-west-1:048378150643:table/GoBotStack-MyTable794EDED1-1CJG90L75PZR3
            )
        )

        api_gateway = apigateway.LambdaRestApi(
            self,
            "GoBotApiGateway",
            handler=gobot_lambda,  # type: ignore
        )

        CfnOutput(self, "ApiGatewayEndpoint", value=api_gateway.url, description="The URL of the GoBot API")
