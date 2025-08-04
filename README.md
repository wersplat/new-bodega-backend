# NBA 2K Global Rankings Backend

A comprehensive FastAPI backend for managing NBA 2K Global Rankings, tournaments, and player profiles, powered by Supabase.

## 🚀 Features

- **Supabase Backend**: Cloud-based PostgreSQL database with real-time capabilities
- **Player Management**: Register, update, and manage player profiles
- **Tournament System**: Create and manage events (Draft, BYOT, Tournaments)
- **Global Rankings**: Real-time leaderboards with tier-based rankings
- **Authentication**: JWT-based authentication with role-based access (via Supabase Auth)
- **Payment Integration**: Stripe checkout for event registrations
- **Discord Bot Integration**: Bot-safe endpoints for Discord integration
- **Admin Panel**: RP updates, badge assignment, and event management
- **Badge System**: Achievement and title system for players
- **Modern Schema Validation**: Pydantic v2 models with strict type checking and validation
- **Structured Logging**: Comprehensive logging with structlog
- **Rate Limiting**: Redis-based rate limiting with configurable limits
- **Error Handling**: Custom exception handling with standardized error responses
- **Monitoring**: Sentry integration for error tracking
- **Development Tools**: Black, isort, mypy, and pytest for code quality

## 🏗️ Project Structure

```
/app
  /routers
    players.py          # Player profile, registration, lookup
    events.py           # Create, list, register for events
    leaderboard.py      # Global & event leaderboards
    auth.py             # Register/login, JWT auth
    admin.py            # RP updates, award assignment
    discord.py          # Discord ID lookups, bot-safe endpoints
    payments.py         # Stripe payment integration
    teams.py            # Team management
    matches.py          # Match results and statistics
    player_stats.py     # Player statistics
  /models               # SQLAlchemy models
  /schemas              # Pydantic v2 schemas with validation
    __init__.py         # Schema package initialization
    badge.py            # Badge and achievement schemas
    event.py            # Event and tournament schemas
    player.py           # Player profile and ranking schemas
    user.py             # User authentication schemas
  /services             # RP calculation, email, webhook logic
  /core                 # App init, config, auth dependencies
    config.py           # Configuration management
    logging.py          # Structured logging setup
    exceptions.py       # Custom exception handling
    supabase.py         # Supabase client and utilities
    rate_limiter.py     # Rate limiting configuration
main.py                 # FastAPI application entry point
requirements.txt        # Python dependencies
pyproject.toml          # Development tools configuration
Dockerfile              # Multi-stage Docker configuration
docker-compose.yml      # Development environment setup
scripts/dev-setup.sh    # Development setup automation
```

## 🔐 Authentication

For detailed authentication documentation, see [AUTHENTICATION.md](docs/AUTHENTICATION.md).

### Key Features
- **JWT-based Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for users, players, and admins
- **Row Level Security**: Fine-grained data access control
- **Token Refresh**: Secure token refresh mechanism

### Quick Start
1. Configure your `.env` file with Supabase credentials
2. Use the `/auth` endpoints to register/login
3. Include the JWT in the `Authorization: Bearer <token>` header

For testing authentication, run:
```bash
python scripts/check_auth.py
```

## 🛠️ Setup

### Prerequisites

- Python 3.9+
- Supabase account (https://supabase.com/)
- Stripe account (for payments)
- Discord bot token (optional)
- Redis (for rate limiting and caching)

### Quick Setup (Recommended)

Use the automated setup script:

```bash
# Clone the repository
git clone <repository-url>
cd new-bodega-backend

# Run the setup script
./scripts/dev-setup.sh
```

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new-bodega-backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

5. **Supabase Setup**
   1. Create a new project at https://supabase.com/
   2. Go to Project Settings > API to find your Project URL and anon/public key
   3. Update `.env` with your Supabase credentials:
      ```
      SUPABASE_URL=your-project-url
      SUPABASE_KEY=your-service-role-key
      SUPABASE_ANON_KEY=your-anon-key
      ```
   4. (Optional) For direct database access, use the connection string from:
      Project Settings > Database > Connection string > URI
      
6. **Database Migrations**
   ```bash
   # Apply database migrations if using SQLAlchemy
   alembic upgrade head
   ```
   
   Note: With Supabase, you can also use the Table Editor in the Supabase dashboard to manage your database schema.

7. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

### Docker Setup

For containerized development:

```bash
# Start all services (app, Redis, PostgreSQL, pgAdmin)
docker-compose up

# Or build and run specific services
docker-compose up app redis
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on the `.env.example` file with the following required variables:

```env
# Environment Configuration
ENVIRONMENT=development  # development, testing, production

# Supabase Configuration (Required)
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Database (Optional: For direct database access)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_API_KEY=your_discord_api_key

# Redis (for rate limiting and caching)
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_ANONYMOUS=10/minute
RATE_LIMIT_AUTHENTICATED=1000/hour
RATE_LIMIT_ADMIN=5000/hour

# Caching
CACHE_TTL=300
CACHE_ENABLED=True

# App
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Players
- `POST /v1/players/` - Register new player profile
- `GET /v1/players/{id}` - Get player profile
- `GET /v1/players/me` - Get current user's profile
- `PATCH /v1/players/me` - Update current user's profile
- `GET /v1/players/search` - Search by gamertag

### Events
- `GET /v1/events/` - List all events
- `GET /v1/events/open` - List open events
- `POST /v1/events/` - Create new event (admin)
- `GET /v1/events/{id}` - Get event details
- `POST /v1/events/{id}/register` - Register for event
- `DELETE /v1/events/{id}/register` - Unregister from event

### Leaderboard
- `GET /v1/leaderboards/global` - Global leaderboard
- `GET /v1/leaderboards/global/top` - Top players
- `GET /v1/leaderboards/tier/{tier}` - Tier-specific leaderboard
- `GET /v1/leaderboards/event/{id}` - Event leaderboard
- `GET /v1/leaderboards/peak` - Peak RP leaderboard

### Admin
- `POST /admin/update-rp` - Update player RP
- `POST /admin/award-badge` - Award badge to player
- `GET /admin/players` - List all players
- `GET /admin/badges` - List all badges

### Discord
- `GET /discord/players/{discord_id}` - Get player by Discord ID
- `POST /discord/players/register` - Register via Discord
- `GET /discord/players/{discord_id}/rank` - Get player rank
- `GET /discord/stats` - Discord integration stats

### Payments
- `POST /payments/create-session` - Create Stripe checkout
- `POST /payments/webhooks/stripe` - Stripe webhook handler
- `GET /payments/session/{id}/status` - Check payment status

## 🎮 Player Tiers

The system uses the following NBA 2K tiers:
- **Bronze** (0-1000 RP)
- **Silver** (1001-2500 RP)
- **Gold** (2501-5000 RP)
- **Platinum** (5001-10000 RP)
- **Diamond** (10001-20000 RP)
- **Pink Diamond** (20001-50000 RP)
- **Galaxy Opal** (50001+ RP)

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (User/Admin)
- Input validation using Pydantic v2 models
- Secure defaults for all configuration options
- API key protection for Discord endpoints
- Stripe webhook signature verification
- Rate limiting with Redis
- Structured logging with sensitive data filtering

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run tests in parallel
pytest -n auto
```

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build production image
docker build --target production -t nba2k-rankings-backend .

# Run container
docker run -p 8000:8000 nba2k-rankings-backend
```

### Production Checklist

1. Set `ENVIRONMENT=production` in environment
2. Use production database and Redis
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use production Stripe keys
6. Configure Sentry for error tracking
7. Set up monitoring and alerting
8. Configure backup strategies

## 📝 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black app/ main.py

# Sort imports
isort app/ main.py

# Type checking
mypy app/

# Linting
flake8 app/

# Security scanning
bandit -r app/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pip install pre-commit
pre-commit install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure code quality checks pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code examples in the routers
- Check the logs for detailed error information