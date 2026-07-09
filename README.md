
# Complete Recommendation System

A production-ready recommendation system built with FastAPI, SQLAlchemy, and SQLite. Features hybrid recommendations (collaborative filtering, content-based, popularity, and skill matching), caching, logging, and comprehensive evaluation.

## Project Overview

This recommendation system provides personalized recommendations using a hybrid approach combining multiple strategies. The system includes:
- REST API built with FastAPI
- Database management with SQLAlchemy ORM
- Hybrid recommendation engine
- Caching for improved performance
- Structured logging with request ID tracking
- Comprehensive test suite
- Evaluation metrics with visualization
- Docker support for easy deployment

## Architecture

The system follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                  │
│  - Endpoints: /health, /recommend/{user_id}, /feedback   │
│  - Middleware: Request ID, Logging                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Engine Layer (Recommendation Logic)       │
│  - Candidate Generator (multiple strategies)            │
│  - Scoring (weighted combination)                        │
│  - Caching (TTLCache)                                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Layer (SQLAlchemy)                │
│  - Models: User, Content, Skill, Interactions           │
│  - Repositories: CRUD operations                         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Database (SQLite)                     │
└─────────────────────────────────────────────────────────┘
```

## Folder Structure

```
Complete Recommendation System/
├── api/
│   ├── __init__.py
│   ├── app.py                 # Main FastAPI application
│   ├── config.py              # Configuration management
│   ├── dependencies.py        # Dependency injection
│   ├── logging_config.py      # Logging configuration
│   ├── middleware.py          # Request ID and logging middleware
│   ├── schemas.py             # Pydantic schemas
│   └── routers/               # API routers
├── data/
│   ├── __init__.py
│   ├── database.py            # Database setup
│   ├── models.py              # SQLAlchemy models
│   └── repository.py          # Repository pattern for CRUD
├── engine/
│   ├── __init__.py
│   ├── base.py                # Base recommender
│   ├── cache.py               # Caching layer
│   ├── candidate_gen.py       # Candidate generation strategies
│   ├── hybrid.py              # Hybrid recommender
│   ├── orchestrator.py        # Recommendation orchestrator
│   ├── scorer.py              # Recommendation scoring
│   └── similarity.py          # Similarity algorithms
├── scripts/
│   ├── __init__.py
│   ├── init_db.py             # Initialize database
│   ├── seed_data.py           # Seed database with sample data
│   ├── test_repositories.py   # Test repository functions
│   └── train_model.py         # Train recommendation models
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures
│   ├── test_api.py            # API endpoint tests
│   ├── test_data.py           # Repository and model tests
│   └── test_engine.py         # Engine component tests
├── Dockerfile                 # Docker build file
├── docker-compose.yml         # Docker Compose configuration
├── evaluate.py                # Evaluation script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── .gitignore                 # Git ignore file
```

## Installation

### Prerequisites
- Python 3.12+
- pip
- Docker (optional, for containerized deployment)

### Local Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/recommendation-system.git
   cd recommendation-system
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate  # Windows (PowerShell)
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   # Copy .env.example if available, or create your own
   cp .env.example .env  # Linux/macOS
   # Or just use the existing .env file
   ```

5. Initialize the database and seed sample data
   ```bash
   python scripts/init_db.py
   python scripts/seed_data.py
   ```

## Running Locally

1. Start the FastAPI application
   ```bash
   uvicorn api.app:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. API documentation is available at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Running with Docker

### Using Docker Compose (Recommended)

1. Build and start the services
   ```bash
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`

3. Stop the services
   ```bash
   docker-compose down
   ```

### Using Docker Only

1. Build the Docker image
   ```bash
   docker build -t recommendation-api .
   ```

2. Run the container
   ```bash
   docker run -d -p 8000:8000 -v $(pwd)/data:/app/data --name recommendation-api recommendation-api
   ```

3. Stop and remove the container
   ```bash
   docker stop recommendation-api
   docker rm recommendation-api
   ```

## API Documentation

### Endpoints

| Method | Endpoint             | Description                                      |
|--------|----------------------|--------------------------------------------------|
| GET    | /health              | Health check endpoint                            |
| GET    | /recommend/{user_id} | Get recommendations for a specific user          |
| POST   | /feedback            | Record user feedback/interaction with content    |
| GET    | /metrics             | Get system metrics (cache stats, etc.)           |
| GET    | /users/              | Get all users                                    |
| POST   | /users/              | Create a new user                                |
| GET    | /content/            | Get all content items                            |
| POST   | /content/            | Create a new content item                        |
| GET    | /skills/             | Get all skills                                   |
| POST   | /skills/             | Create a new skill                               |
| GET    | /interactions/       | Get all interactions                             |
| POST   | /interactions/       | Create a new interaction                         |

For detailed API documentation, visit the Swagger UI at `http://localhost:8000/docs` when the application is running.

## Evaluation Metrics

To evaluate the recommendation system, run the evaluation script:
```bash
python evaluate.py
```

This will generate:
- `evaluation_report.md`: Detailed evaluation metrics report
- `evaluation_metrics_chart.png`: Bar chart visualizing the metrics

The following metrics are computed:
- **Precision@5**: Proportion of relevant items in top 5 recommendations
- **Recall@5**: Proportion of all relevant items that appear in top 5
- **NDCG@5**: Normalized Discounted Cumulative Gain at 5
- **Coverage**: Proportion of all items that appear in recommendations
- **Diversity**: Average pairwise dissimilarity of recommended items
- **Novelty**: Measure of how unexpected the recommended items are

## Testing

Run the test suite with pytest:
```bash
pytest tests/ -v
```

To run tests with coverage:
```bash
pytest tests/ -v --cov=api --cov=data --cov=engine --cov-report=term-missing
```

## Future Improvements

1. **Database Upgrade**: Switch from SQLite to PostgreSQL/MySQL for better performance and scalability
2. **Real-time Updates**: Implement WebSocket support for real-time recommendations
3. **A/B Testing**: Add support for A/B testing different recommendation strategies
4. **User Profiles**: Implement user profile management and preference settings
5. **Advanced NLP**: Add text-based recommendations using NLP for content descriptions
6. **Graph Database**: Use a graph database (e.g., Neo4j) for better collaborative filtering
7. **Monitoring**: Add Prometheus/Grafana for monitoring and observability
8. **Authentication**: Add user authentication (OAuth2, JWT) to secure the API

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
