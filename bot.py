import asyncio
import os
import httpx
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ── FastAPI server ──────────────────────
fastapi_app = FastAPI()

@fastapi_app.post("/chat")
async def chat(body: dict):
    user_message = body.get("message")
    print(f"Server received: {user_message}")
    reply = f"Server got your message: {user_message}"
    return {"reply": reply}


# ── Telegram bot ────────────────────────
async def handle_message(update: Update, context):
    user_message = update.message.text

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={"message": user_message}
        )
        data = response.json()

    await update.message.reply_text(data.get("reply"))


# ── Run both together ───────────────────
async def main():
    # FastAPI server config
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    # Telegram bot config
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Initialize and start bot manually (not run_polling)
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()

    # Run FastAPI (this blocks until you stop)
    await server.serve()

    # When FastAPI stops, stop bot cleanly
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())