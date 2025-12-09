# BookWorm

A modern, full-stack web application for managing your personal book collection. Track your reading progress, rate books, write reviews, and discover new titles through ISBN search.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Book Management**: Browse books, search by ISBN using Open Library API
- **Personal Bookshelf**: Add books to your shelf, track reading status
- **Reading Progress**: Set status (Plan to Read, Reading, Completed, Dropped)
- **Reviews & Ratings**: Rate books (1-5 stars) and write detailed reviews
- **Admin Panel**: User management and book deletion (ADMIN role)
- **Profile Management**: Update your profile, manage account settings

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - ORM for database operations (async support)
- **PostgreSQL** - Relational database
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **JWT** (python-jose) - Token-based authentication
- **bcrypt** - Password hashing
- **httpx** - Async HTTP client for external API calls

### Frontend
- **Jinja2** - Server-side templating
- **Tailwind CSS** - Utility-first CSS framework
- **Vanilla JavaScript** - No framework dependencies
- **Font Awesome** - Icon library

## Project Structure

```
BookWorm/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
├── .env                    # Environment variables (not in git)
├── docker-compose.yaml    # Docker configuration
│
├── alembic/               # Database migrations
│   ├── env.py
│   └── versions/
│
└── app/                   # Main application package
    ├── models.py          # SQLAlchemy database models
    ├── schemas.py         # Pydantic validation schemas
    ├── database.py        # Database connection configuration
    ├── security.py        # JWT and password hashing
    ├── settings.py        # Application settings (from .env)
    ├── dependencies.py   # FastAPI dependencies
    │
    ├── routers/           # API endpoints
    │   ├── auth.py        # Authentication (login, register)
    │   ├── books.py       # Books CRUD + ISBN search
    │   ├── shelf.py       # Shelf items CRUD
    │   └── users.py       # Users CRUD
    │
    ├── templates/         # HTML templates (Jinja2)
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   ├── browse.html
    │   ├── dashboard.html
    │   └── profile.html
    │
    └── static/            # Static files (CSS, JS)
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 15+
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd BookWorm
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookworm

SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Change `SECRET_KEY` to a secure random string in production!

### Step 5: Set Up Database

#### Option A: Using Docker Compose

```bash
docker-compose up -d
```

#### Option B: Manual PostgreSQL Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE bookworm;
```

2. Update `.env` with your database credentials

### Step 6: Run Database Migrations

```bash
alembic upgrade head
```

### Step 7: Start the Application

```bash
uvicorn main:app --reload
```

The application will be available at:
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Usage

### Registration

1. Navigate to http://localhost:8000/register
2. Fill in username, email, and password
3. Click "Sign Up"
4. You will be redirected to the login page

### Login

1. Navigate to http://localhost:8000/login
2. Enter your credentials
3. You will receive a JWT token (stored in localStorage)
4. Redirected to the dashboard

### Browse Books

1. Go to `/browse`
2. View all available books
3. Search by title/author using the search bar
4. Search by ISBN using the ISBN search field (queries Open Library API)
5. Click "Add to Shelf" to add books to your collection

### Manage Your Shelf

1. Go to `/dashboard` (My Shelf)
2. View all books on your shelf
3. Update reading status (Plan to Read, Reading, Completed, Dropped)
4. Rate books (1-5 stars)
5. Write reviews
6. Remove books from shelf

### Profile Management

1. Go to `/profile`
2. Update username and email
3. **Admin users**: Change user roles and manage all users

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login (get JWT token)
- `GET /auth/me` - Get current user info

### Books (`/books`)
- `GET /books/` - List all books (pagination: `?skip=0&limit=100`)
- `GET /books/{book_id}` - Get book by ID
- `PUT /books/{book_id}` - Update book (authenticated)
- `DELETE /books/{book_id}` - Delete book (ADMIN only)
- `POST /books/search-by-isbn` - Search book by ISBN (Open Library API)

### Shelf (`/shelf`)
- `GET /shelf/` - Get user's shelf items
- `GET /shelf/{item_id}` - Get shelf item by ID
- `POST /shelf/` - Add book to shelf
- `PUT /shelf/{item_id}` - Update shelf item (status, rating, review)
- `DELETE /shelf/{item_id}` - Remove book from shelf

### Users (`/users`)
- `GET /users/` - List all users (ADMIN only)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user (own profile or ADMIN)
- `DELETE /users/{user_id}` - Delete user (ADMIN only)

## Database Schema

### Tables

- **users**: User accounts (id, username, email, hashed_password, role)
- **books**: Book catalog (id, title, author, isbn, description, cover_url)
- **shelf_items**: User-book relationships (id, user_id, book_id, status, rating, review)

### Relationships

- **1:N**: User → ShelfItem (one user has many shelf items)
- **1:N**: Book → ShelfItem (one book can be on many shelves)
- **N:M**: User ↔ Book (many-to-many via ShelfItem junction table)

## Authentication

The application uses **JWT (JSON Web Tokens)** for authentication:

1. User logs in via `POST /auth/token`
2. Server generates JWT token containing:
   - `sub`: User ID
   - `username`: Username
   - `role`: User role (USER/ADMIN)
3. Token stored in browser localStorage
4. Token included in `Authorization: Bearer <token>` header for protected endpoints
5. Token expires after 30 minutes (configurable)

## Admin Features

Users with `ADMIN` role have access to:

- **Book Deletion**: Delete books from the catalog (`/browse` page)
- **User Management**: View all users, change roles, delete accounts (`/profile` page)
- **Role Management**: Modify user roles (USER ↔ ADMIN)

## External API Integration

### Open Library API

The application integrates with [Open Library](https://openlibrary.org/) for ISBN-based book search:

- Endpoint: `POST /books/search-by-isbn`
- Searches by ISBN: `https://openlibrary.org/isbn/{isbn}.json`
- Automatically fetches:
  - Title
  - Author (with additional API call if needed)
  - Description
  - Cover image URL
- Books are stored in the database for future use

## Development

### Running Migrations

```bash
# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where possible
- No comments in code (as per project requirements)
- All text in English

## Security Considerations

- Passwords are hashed using bcrypt (never stored in plain text)
- JWT tokens use secure secret key (stored in `.env`)
- SQL injection prevented by using SQLAlchemy ORM
- XSS protection via Jinja2 template escaping
- Role-based access control (RBAC) for admin features
- Input validation using Pydantic schemas

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `docker-compose ps` or `pg_isready`
- Check `.env` file has correct database credentials
- Ensure database exists: `psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='bookworm';"`

### Migration Errors

- Check Alembic configuration in `alembic/env.py`
- Verify `settings.DATABASE_URL` is correctly set
- Try: `alembic current` to see current migration version

### Token Issues

- Clear browser localStorage: `localStorage.clear()`
- Check token expiration (default: 30 minutes)
- Verify `SECRET_KEY` in `.env` matches the one used to create tokens

## License

This project is part of a university assignment (Debreceni Egyetem).

## Author

Pisti - Debreceni Egyetem Projekt

---

For detailed API documentation, visit http://localhost:8000/docs after starting the application.

