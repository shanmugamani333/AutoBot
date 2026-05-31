"""
Run once to register the Telegram webhook URL.
docker compose exec api python -m bot.register_webhook
"""
import asyncio
import httpx
from api.config import get_settings

settings = get_settings()


async def register():
    url = (
        f"https://api.telegram.org/bot{settings.telegram_bot_token}"
        f"/setWebhook?url={settings.telegram_webhook_url}/webhook"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        if data.get("ok"):
            print(f"Webhook registered: {settings.telegram_webhook_url}/webhook")
        else:
            print(f"Failed: {data}")


if __name__ == "__main__":
    asyncio.run(register())
