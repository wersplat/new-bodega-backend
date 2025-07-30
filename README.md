# NBA 2K Global Rankings Backend

A comprehensive FastAPI backend for managing NBA 2K Global Rankings, tournaments, and player profiles.

## 🚀 Features

- **Player Management**: Register, update, and manage player profiles
- **Tournament System**: Create and manage events (Draft, BYOT, Tournaments)
- **Global Rankings**: Real-time leaderboards with tier-based rankings
- **Authentication**: JWT-based authentication with role-based access
- **Payment Integration**: Stripe checkout for event registrations
- **Discord Bot Integration**: Bot-safe endpoints for Discord integration
- **Admin Panel**: RP updates, badge assignment, and event management
- **Badge System**: Achievement and title system for players

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
  /models               # SQLAlchemy models
  /schemas              # Pydantic schemas
  /services             # RP calculation, email, webhook logic
  /core                 # App init, config, auth dependencies
main.py
alembic/               # Database migrations
```

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Stripe account (for payments)
- Discord bot token (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new-bodega-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb nba2k_rankings
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/nba2k_rankings

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_API_KEY=your_discord_api_key

# App
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
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
- `POST /players/` - Register new player profile
- `GET /players/{id}` - Get player profile
- `GET /players/me/profile` - Get current user's profile
- `PUT /players/me/profile` - Update current user's profile
- `GET /players/search/{gamertag}` - Search by gamertag

### Events
- `GET /events/` - List all events
- `GET /events/open` - List open events
- `POST /events/` - Create new event (admin)
- `GET /events/{id}` - Get event details
- `POST /events/{id}/register` - Register for event
- `DELETE /events/{id}/register` - Unregister from event

### Leaderboard
- `GET /leaderboard/global` - Global leaderboard
- `GET /leaderboard/global/top` - Top players
- `GET /leaderboard/tier/{tier}` - Tier-specific leaderboard
- `GET /leaderboard/event/{id}` - Event leaderboard
- `GET /leaderboard/peak` - Peak RP leaderboard

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
- API key protection for Discord endpoints
- Stripe webhook signature verification

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t nba2k-rankings-backend .

# Run container
docker run -p 8000:8000 nba2k-rankings-backend
```

### Production

1. Set `DEBUG=False` in environment
2. Use production database
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use production Stripe keys

## 📝 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code examples in the routers 