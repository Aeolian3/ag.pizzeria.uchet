# Inventorization Telegram Bot

A Telegram bot application for inventory management. This bot helps organizations track their inventory, manage products, categories, and inventory sessions.

## Features

- Organization management
- Product and category tracking
- Inventory session management
- User management with different roles
- Reporting capabilities

## Prerequisites

- Python 3.9+
- PostgreSQL or another SQLAlchemy-compatible database
- Telegram Bot Token (from BotFather)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Inventorization.git
   cd Inventorization
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Linux/Mac
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=your_database_url
   ```

   For PostgreSQL, the DATABASE_URL format is:
   ```
   postgresql+asyncpg://username:password@host:port/database_name
   ```

5. Initialize the database:
   ```
   alembic upgrade head
   ```

## Running the Bot

To start the bot, run:
```
python main.py
```

## Docker Deployment

You can also run the bot using Docker:

```
docker build -t inventorization-bot .
docker run -d --name inventorization-bot --env-file .env inventorization-bot
```

## Project Structure

- `admin/` - Admin commands and utilities
- `alembic/` - Database migration scripts
- `database/` - Database connection and session management
- `handlers/` - Telegram bot command handlers
- `middleware/` - Middleware components
- `models/` - SQLAlchemy ORM models
- `states/` - State management for conversation flows
- `template/` - Report templates
- `utils/` - Utility functions

## Development

To add new features or fix bugs:

1. Create a new branch
2. Make your changes
3. Run tests (if available)
4. Submit a pull request

## License

[Specify your license here]

