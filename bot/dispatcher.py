"""
Bot dispatcher — receives a raw Telegram update dict and routes it.

Day 0: just echoes messages back.
Week 2 onwards: this calls the intent classifier and module router.
"""

import structlog
from api.config import settings
import httpx

log = structlog.get_logger()

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> None:
    """Send a text message back to the user via Telegram Bot API."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id":    chat_id,
                "text":       text,
                "parse_mode": parse_mode,
            },
            timeout=10,
        )


async def dispatch(update: dict) -> None:
    """
    Main dispatcher — called for every incoming Telegram update.

    Current state (Day 0): echoes the message back.
    Will grow week by week as modules are added.
    """
    message = update.get("message") or update.get("edited_message")
    if not message:
        log.info("update_ignored", update_id=update.get("update_id"))
        return

    chat_id     = message["chat"]["id"]
    user        = message.get("from", {})
    telegram_id = user.get("id", chat_id)
    first_name  = user.get("first_name", "there")

    log.info(
        "message_received",
        telegram_id=telegram_id,
        chat_id=chat_id,
        has_text=bool(message.get("text")),
        has_photo=bool(message.get("photo")),
    )

    # ── /start command ────────────────────────────────────────────────────────
    text = message.get("text", "")
    if text.strip() == "/start":
        await send_message(
            chat_id,
            f"👋 Hello {first_name}! Welcome to *{settings.STORE_NAME}*.\n\n"
            f"I can help you with:\n"
            f"• Check product availability and prices\n"
            f"• Get product recommendations\n"
            f"• Raise a dispute (price mismatch, expired item etc.)\n"
            f"• Check your loyalty points and offers\n\n"
            f"Just send me a message or a photo of a product!",
        )
        return

    # ── /help command ─────────────────────────────────────────────────────────
    if text.strip() == "/help":
        await send_message(
            chat_id,
            "*What I can do:*\n\n"
            "🔍 *Inventory* — \"do you have oats?\"\n"
            "💡 *Recommend* — \"something high in protein under $5\"\n"
            "⚠️ *Dispute* — \"the shelf price was wrong\"\n"
            "🎁 *Points* — \"how many points do I have?\"\n"
            "🏷️ *Offers* — \"what are today's deals?\"\n\n"
            "_I only answer store-related questions._",
        )
        return

    # ── Day 0: Echo (will be replaced in Week 2) ──────────────────────────────
    if text:
        await send_message(
            chat_id,
            f"📨 You said: _{text}_\n\n"
            f"_(Bot is being set up. Full features coming soon!)_",
        )
    elif message.get("photo"):
        await send_message(
            chat_id,
            "📷 Got your photo!\n\n"
            "_(Image processing coming in Week 3!)_",
        )
    else:
        await send_message(
            chat_id,
            "I received your message. Full features coming soon!",
        )
