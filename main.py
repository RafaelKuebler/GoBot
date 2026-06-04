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

    logger.info(
        "Running in lambda... source=%s path=%s keys=%s",
        (event.get("requestContext", {}) or {}).get("http", {}).get("sourceIp"),
        (event.get("requestContext", {}) or {}).get("http", {}).get("path") or event.get("rawPath"),
        list(event.keys()),
    )
    return asyncio.run(async_handler(event, application))
    # return asyncio.get_event_loop().run_until_complete(async_handler(event, application))


async def async_handler(event, application: Application):
    try:
        body = event.get("body")
        if not body:
            logger.warning(
                "Invocation with no body. event=%s",
                {k: v for k, v in event.items() if k != "headers"},
            )
            return {"statusCode": 400, "body": "No body"}
        update = Update.de_json(json.loads(body), application.bot)
        logger.info("Processing update_id=%s", getattr(update, "update_id", None))
        await application.initialize()
        await application.process_update(update)
        return {"statusCode": 200, "body": "Success"}
    except Exception as exc:
        logger.exception("async_handler failed: %s", exc)
        return {"statusCode": 500, "body": str(exc)}


def main():
    application = setup_app()

    logger.info("Start polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
