# Autonomous Store Bot

Telegram bot for a physical autonomous store.
Features: inventory query, product recommendations, dispute management, loyalty points, offers.

## Stack
- Python 3.11 + FastAPI
- Ollama (Mistral 7B + LLaVA 1.6 + nomic-embed-text)
- PostgreSQL 15 + pgvector
- Redis 7
- Celery (async tasks)
- Docker Compose

## Quick Start

```bash
# 1. Copy env file
cp .env.example .env
# Fill in TELEGRAM_BOT_TOKEN

# 2. Pull Ollama models (one-time, takes ~10 min)
docker compose run --rm ollama ollama pull mistral
docker compose run --rm ollama ollama pull llava
docker compose run --rm ollama ollama pull nomic-embed-text

# 3. Start everything
docker compose up -d

# 4. Run DB migrations
docker compose exec api alembic upgrade head

# 5. Seed sample products
docker compose exec api python -m db.seed

# 6. Register Telegram webhook
docker compose exec api python -m bot.register_webhook
```

## Project Structure
```
store-bot/
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # all settings from env
│   ├── routes/              # webhook, health endpoints
│   ├── modules/             # inventory, recommend, dispute, loyalty, offers
│   ├── llm/                 # ollama client, prompts, embeddings
│   ├── db/                  # models, migrations, seed
│   └── guardrails/          # scope filter, confidence gate, injection guard
├── bot/
│   └── handler.py           # telegram message dispatcher
├── tests/
│   ├── unit/
│   ├── integration/
│   └── adversarial/
├── infra/
│   ├── prometheus.yml
│   └── grafana/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
└── .env.example
```

## Week Plan
- Week 1: DB schema + bot shell
- Week 2: LLM core + intent classifier + scope filter
- Week 3: Inventory module
- Week 4: Recommendation module
- Week 5: Dispute module
- Week 6: Loyalty points module
- Week 7: Offers module + integration
- Week 8: Adversarial testing
- Week 9: Dockerize + cloud deploy
- Week 10: Hardening + production sign-off
