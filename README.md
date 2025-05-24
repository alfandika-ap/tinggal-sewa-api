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

| Endpoint                       | Method | Description                                    |
| ------------------------------ | ------ | ---------------------------------------------- |
| `/api/customer/register`       | POST   | Register a new customer                        |
| `/api/customer/login`          | POST   | Login and get authentication token             |
| `/api/customer/profile`        | GET    | Get customer profile (requires authentication) |
| `/api/customer/bookmarks`      | GET    | List all bookmarks for the authenticated user  |
| `/api/customer/bookmarks`      | POST   | Create a new bookmark with kost details        |
| `/api/customer/bookmarks/{id}` | GET    | Get details of a specific bookmark             |
| `/api/customer/bookmarks/{id}` | DELETE | Remove a bookmark                              |

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

5. Run the development server and chroma
   ```
   python manage.py runserver
   chroma run --port 8010 --path ./vectordata
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

### Notes

Add to bookmark payload example

```
{
  "title": "Kost Singgahsini Safana Unpad",
  "address": "Jalan Raya Jatinangor",
  "city": "Sumedang",
  "province": "Jawa Barat",
  "description": "Kost ini terdiri dari 2 lantai. Tipe kamar B berada di setiap lantainya dengan sebagian jendela menghadap ke arah luar dan sebagian menghadap ke arah koridor.",
  "price": 1022500,
  "facilities": ["WiFi", "AC", "Parking"],
  "rules": ["No Smoking", "No Pets"],
  "contact": "081234567890",
  "url": "https://mamikos.com/room/kost-kabupaten-sumedang-kost-putri-murah-kost-singgahsini-safana-unpad-tipe-b-jatinangor-sumedang",
  "image_url": "https://placehold.co/200x300", // optional
  "gender": "male"
}
```

## License

[Your chosen license]
