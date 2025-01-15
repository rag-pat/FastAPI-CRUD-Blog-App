# FastAPI Blog API

A robust REST API built with FastAPI for managing blog posts with user authentication, rate limiting, and search capabilities.

## 🚀 Features

* User authentication with JWT tokens
* Post management (create, read, search, delete)
* Rate limiting for API endpoints
* Soft delete functionality for posts
* SQLAlchemy ORM integration
* Pydantic schemas for request/response validation

## 🛠️ Technology Stack

* **FastAPI** - Modern, fast web framework for building APIs
* **SQLAlchemy** - SQL toolkit and ORM
* **Pydantic** - Data validation using Python type annotations
* **PassLib** - Password hashing
* **Python-Jose** - JWT token handling
* **SlowAPI** - Rate limiting

## 📋 API Endpoints

### Authentication
* `POST /register` - Register a new user
* `POST /token` - Login and receive access token

### Posts
* `GET /posts` - List all posts (rate limited to 5 requests/minute)
* `GET /search/posts` - Search posts by title or content
* `GET /user/posts` - Get posts for authenticated user
* `DELETE /posts/{id}` - Soft delete a post

## 🚦 Getting Started

1. Clone the repository
```bash
git clone <repository-url>
cd <project-name>
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up the database
```bash
# Update DATABASE_URL in database.py with your database configuration
# Default uses SQLite: "sqlite:///./test.db"
```

4. Run the application
```bash
uvicorn main:app --reload
```

## ⚙️ Configuration

Key configurations are stored in respective files:

* `database.py` - Database connection settings
* `auth.py` - JWT secret key and algorithm
* `main.py` - Rate limiting rules

### Environment Variables
```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key
```

## 🔒 Security Features

* Password hashing using bcrypt
* JWT token-based authentication
* Rate limiting to prevent abuse
* Soft delete implementation
* Input validation using Pydantic models

## 🗄️ Database Schema

### User Table
* id (Integer, Primary Key)
* username (String, Unique)
* password_hash (String)

### Post Table
* id (Integer, Primary Key)
* title (String)
* content (String)
* published (Boolean)
* deleted_at (DateTime)
* owner_id (Integer, Foreign Key)

## 📚 API Documentation

Once the application is running, visit:
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

## 🔍 Query Parameters

* `skip`: Number of records to skip (pagination)
* `limit`: Maximum number of records to return
* `query`: Search term for post search endpoint

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE.md file for details
