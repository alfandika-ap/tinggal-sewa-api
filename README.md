# Tinggal Sewa Backend

Backend service for the Tinggal Sewa application - a property rental platform.

## Features

- Customer registration and authentication
- Customer profile management
- Token-based authentication
- RESTful API design

## Tech Stack

- Django 5.2.1
- Django REST Framework 3.16.0
- SQLite (development)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/customer/register` | POST | Register a new customer |
| `/api/customer/login` | POST | Login and get authentication token |
| `/api/customer/profile` | GET | Get customer profile (requires authentication) |

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/tinggal-sewa-be.git
   cd tinggal-sewa-be
   ```

2. Create and activate a virtual environment
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations
   ```
   python manage.py migrate
   ```

5. Run the development server
   ```
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`.

## Development

### Create a superuser

```
python manage.py createsuperuser
```

### Running tests

```
python manage.py test
```

## License

[Your chosen license] 