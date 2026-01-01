# LeagueScraper

A FastAPI-based web scraper service for fetching football match lineup data from SofaScore. The service provides a RESTful API to retrieve detailed player lineups, statistics, and match information.

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional, for containerized deployment)
- pip (Python package manager)

## Installation

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/LeagueScraper.git
cd LeagueScraper
```

2. **Create a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables (optional):**
```bash
export BASE_URL=https://www.sofascore.com  # Default value
```

5. **Run the application:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Or build and run with Docker:**
```bash
docker build -t leaguescraper .
docker run -p 8000:8000 leaguescraper
```

## API Usage

### Get Match Lineup

**Endpoint:** `POST /api/v1/football/match/lineup`

**Request Body:**
```json
{
  "team1": "olympic-safi",
  "team2": "wydad-casablanca"
}
```

**Response:**
```json
{
  "lineup": {
    "confirmed": true,
    "home": {
      "players": [...],
      "formation": "4-4-2"
    },
    "away": {
      "players": [...],
      "formation": "4-3-3"
    }
  }
}
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_match_lineup_api.py -v
```

## Project Structure

```
LeagueScraper/
├── app/
│   ├── api/
│   │   ├── endpoints/      # API endpoints
│   │   └── routers/         # Route configuration
│   ├── core/                # Core configuration
│   ├── services/            # Business logic services
│   └── main.py              # FastAPI application
├── tests/                   # Test files
├── .github/workflows/       # CI/CD workflows
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── pytest.ini              # Pytest configuration
```

## CI/CD

The project includes GitHub Actions workflows for:

- **CI**: Automated testing on push/PR
- **CD**: Docker image building and deployment (Still not implemented with AWS)

See [.github/workflows/README.md](.github/workflows/README.md) for details.

## Development

1. **Fork the repository**
2. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes and run tests:**
```bash
pytest tests/ -v
```

4. **Commit your changes:**
```bash
git commit -m 'Add some feature'
```

5. **Push to the branch:**
```bash
git push origin feature/your-feature-name
```

6. **Open a Pull Request**

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | SofaScore base URL | `https://www.sofascore.com` |

## Technologies

- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **Zendriver**: Browser automation
- **Pytest**: Testing framework
- **Docker**: Containerization

## License

This project is open source and available for educational and development purposes.

