"""
Telegram bot entry point.
Week 1: receive messages, log them, forward to API webhook.
Week 2+: full intent routing added.
"""
import asyncio
import httpx
import structlog
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler

from api.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

API_WEBHOOK_URL = f"{settings.__dict__.get('api_base_url', 'http://api:8000')}/webhook"


async def handle_message(update: Update, context) -> None:
    """Forward every message to FastAPI for processing."""
    if not update.message:
        return

    user = update.message.from_user
    logger.info(
        "message_received",
        telegram_id=str(user.id),
        username=user.username,
        has_text=bool(update.message.text),
        has_photo=bool(update.message.photo),
    )

    # Forward to FastAPI
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = update.to_dict()
            resp = await client.post(API_WEBHOOK_URL, json=payload)
            data = resp.json()

        reply_text = data.get("reply", "I received your message.")
        await update.message.reply_text(reply_text)

    except Exception as e:
        logger.error("handler_error", error=str(e))
        await update.message.reply_text(
            "Something went wrong. Please try again."
        )


async def handle_start(update: Update, context) -> None:
    await update.message.reply_text(
        "Welcome to the store assistant!\n\n"
        "You can ask me about:\n"
        "- Product availability and prices\n"
        "- Product recommendations\n"
        "- Raise a dispute\n"
        "- Check your loyalty points\n"
        "- Current offers\n\n"
        "Just type your question or send a photo of a product."
    )


def main():
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    logger.info("bot_starting", mode="polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
