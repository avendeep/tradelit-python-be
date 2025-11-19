# TradeLit - Algo Trading Application

A FastAPI-based algorithmic trading application with MongoDB integration.

## Project Structure

```
tradeLit_app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       └── router.py       # API router configuration
│   ├── core/                   # Core configurations
│   │   ├── config.py          # Application settings
│   │   └── security.py        # Security utilities
│   ├── db/                     # Database configurations
│   │   └── mongodb.py         # MongoDB connection
│   ├── models/                 # Database models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── utils/                  # Utility functions
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## Setup

1. **Create a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the values as needed

4. **Ensure MongoDB is running:**
   - Default connection: `mongodb://localhost:27017`
   - Database name: `trade_lit_db`

## Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Features

- FastAPI framework with async support
- MongoDB integration using Motor (async driver)
- **Upstox API Integration with OAuth 2.0 authentication** 🆕
- Organized project structure
- Environment-based configuration
- API versioning (v1)
- Auto-generated API documentation (Swagger UI)

## 🔐 Upstox Integration

TradeLit now includes full Upstox broker API integration for live trading with **persistent authentication** that survives server restarts.

**Quick Links:**

- **[Quick Start Guide](UPSTOX_QUICKSTART.md)** - Get started in 5 minutes
- **[Token Persistence](TOKEN_PERSISTENCE.md)** - How authentication persistence works 🆕
- **[Option Chain API](OPTION_CHAIN_API.md)** - Fetch option chains 🆕
- **[Detailed Documentation](UPSTOX_INTEGRATION.md)** - Complete integration guide
- Test your setup: `python test_upstox_setup.py`

**Features:**

- OAuth 2.0 authentication flow
- Token management with auto-validation
- **MongoDB token persistence** - Stay authenticated across restarts 🆕
- **Auto-load on startup** - Tokens loaded automatically 🆕
- **Option Chain API** - Fetch complete put/call option chains 🆕
- User profile access
- Pre-configured API client for Upstox SDK
