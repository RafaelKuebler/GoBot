from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from aws_cdk.aws_ecr_assets import DockerImageAsset
from cdk_ecr_deployment import DockerImageName, ECRDeployment
from constructs import Construct

from gobot.settings import get_settings


class GoBotStack(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        s = get_settings()

        repo = ecr.Repository(
            self,
            "Repo",
            repository_name="gobot",
            lifecycle_rules=[ecr.LifecycleRule(max_image_count=1)],
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True,
        )
        image = DockerImageAsset(self, "Image", directory="..")
        push = ECRDeployment(
            self,
            "PushImage",
            src=DockerImageName(image.image_uri),
            dest=DockerImageName(f"{repo.repository_uri}:{image.asset_hash}"),
        )

        gobot_lambda = _lambda.DockerImageFunction(
            self,
            id="GoBotLambda",
            function_name="GoBotLambda",
            code=_lambda.DockerImageCode.from_ecr(
                repository=repo,
                tag_or_digest=image.asset_hash,
            ),
            environment={
                "TOKEN": s.TOKEN,
            },
            log_group=logs.LogGroup(
                self,
                "LogGroup",
                log_group_name="/aws/lambda/GoBotLambda",
                retention=logs.RetentionDays.ONE_WEEK,
                removal_policy=RemovalPolicy.DESTROY,
            ),
            architecture=_lambda.Architecture.ARM_64,
            timeout=Duration.seconds(15),
        )
        gobot_lambda.node.add_dependency(push)

        dynamodb_table = dynamodb.Table(
            self,
            "GobotGamesDynamoDBTable",
            table_name="gobot_games",
            partition_key=dynamodb.Attribute(
                name="chat_id",
                type=dynamodb.AttributeType.NUMBER,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
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
            )
        )

        api_gateway = apigateway.LambdaRestApi(
            self,
            "GoBotApiGateway",
            handler=gobot_lambda,  # type: ignore
        )

        CfnOutput(self, "ApiGatewayEndpoint", value=api_gateway.url, description="The URL of the GoBot API")
