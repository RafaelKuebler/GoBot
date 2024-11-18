import asyncio
import json
import logging

from telegram import Update
from telegram.ext import Application

from gobot.log_utils import setup_logging
from gobot.telegram.telegram_interface import setup_app

logger = logging.getLogger(__name__)

setup_logging()


# handler for AWS Lambda
def lambda_handler(event, context):
    """Called when AWS Lambda is triggered"""
    application = setup_app()

    logger.info("Running in lambda...")
    return asyncio.get_event_loop().run_until_complete(async_handler(event, application))


async def async_handler(event, application: Application):
    try:
        await application.initialize()
        await application.process_update(Update.de_json(json.loads(event["body"]), application.bot))
        return {"statusCode": 200, "body": "Success"}
    except Exception as exc:
        return {"statusCode": 500, "body": str(exc)}


def main():
    application = setup_app()

    logger.info("Start polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
