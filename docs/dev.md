# GoBot Dev Docs

This is the developer documentation for the **GoBot** project.
It should walk you through everything necessary to set up the project locally and/or deploy to AWS.

## Project setup
To get an overview of supported [make](https://www.gnu.org/software/make/) commands, run `make help`.
To see how each task is configured, see the [`Makefile`](/Makefile).

To get your local dev environment up and running, use `make setup`.
This will set up a virtual environment for you and install all dependencies, as well as pre-commit hooks.

All tooling is configured in the [`pyproject.toml`](/pyproject.toml) file.
To run all pre-commit hooks on all files, run `make pre-commit`.

## GUI
There is a simple [tkinter](https://docs.python.org/3/library/tkinter.html) GUI implementation that can be started running `make gui`.
It was meant to test and debug the Go rules implementation.
Left- or right-clicking sets stones (there are no turns, which saves time when manually testing certain scenarios!)

### .env file
To store secrets and other configuration, you need to create your own `.env` file.
For this you can copy and rename the [`.env.template`](/.env.template) file and fill your Telegram bot `TOKEN`.

The app uses [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to parse and validate the `.env` file and environment variables.
The settings class is defined under [`gobot/settings.py`](/gobot/settings.py)

## AWS Deployment
The bot can be deployed to AWS via the `make deploy` command.

To provision the necessary resources, a CDK stack is set up that includes the `gobot_games` DynamoDB table, a (Docker-based) Lambda function, the API gateway that accepts the webhooks calls, and all necessary IAM permissions.
If it is your first time deploying via CDK to your account you will have to [bootstrap your environment](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html).

The CDK code can be found in the [infrastructure](/infrastructure) folder.

After deployment, `make deploy` will automatically set up the webhook for your Telegram bot through the API, pointing it to the API Gateway.

## Architecture
The app is designed to be runnable both locally to poll from the Telegram Bot API or on the cloud as serveless function triggered via webhook.
For this, it offers two entry points which can be inspected in the [`main.py`](/main.py) file.

To make the serverless function case possible, the application maintains no internal state or cache of the games and persists all data to a database.
The DB of choice is [AWS DynamoDB](https://aws.amazon.com/dynamodb/), a serverless, No-SQL database.

Therefore, when running locally or in the cloud, a running DynamoDB s required.
When running locally via `make run`, a local Docker container is automatically started that simulates the DynamoDB.

When running in the cloud, the application will identify your DynamoDB by itself, but requires an existing table named `gobot-games`.
