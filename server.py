from fastapi import FastAPI

app = FastAPI()


@app.post("/chat")
async def chat(body: dict):
    user_message = body.get("message")
    print(f"Server received: {user_message}")

    reply = f"Server got your message: {user_message}"
    return {"reply": reply}