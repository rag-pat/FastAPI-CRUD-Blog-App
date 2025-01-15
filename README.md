# FastAPI-CRUD-Blog-App

# FastAPI CRUD Blog App

This is a simple FastAPI application designed for learning and practicing CRUD operations, API development, user authentication, and rate limiting. The app serves as a blog platform where users can register, log in, create posts, search for posts, and soft-delete them. It also includes token-based authentication for secure access.

---

## 📖 Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [User Routes](#user-routes)
  - [Post Routes](#post-routes)
- [Project Structure](#project-structure)
- [Learning Goals](#learning-goals)
- [License](#license)

---

## 🛠️ Features
- **User Authentication**
  - User registration and login with hashed passwords.
  - JWT-based token generation for secure access.
- **Post Management**
  - Create, read, search, and soft-delete posts.
  - Search posts by title or content.
- **Rate Limiting**
  - Restricts excessive requests to the `/posts` endpoint.
- **Soft Deletion**
  - Posts are not permanently deleted; instead, they are marked as deleted.
- **SQLAlchemy Integration**
  - Database ORM for managing users and posts.
- **FastAPI**
  - Lightweight framework for rapid API development.

---

## 🛠️ Technologies Used
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite (default) with SQLAlchemy ORM.
- **Authentication**: JWT (JSON Web Tokens) with `python-jose`.
- **Password Hashing**: Passlib (Bcrypt).
- **Rate Limiting**: SlowAPI.

---

## 🚀 Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/fastapi-crud-blog-app.git
   cd fastapi-crud-blog-app
Create a Virtual Environment

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Run the App

bash
Copy code
uvicorn app.main:app --reload
Access the App Open your browser and go to http://127.0.0.1:8000/docs to view the Swagger documentation.

🎮 Usage
1. User Registration
Register a new user by sending a POST request to /register.
Provide a username and password.
2. Log In
Obtain a JWT access token by sending a POST request to /token with valid credentials.
Manage Posts
Use your JWT token to create, search, view, and soft-delete posts.

🌐 API Endpoints
🔑 Authentication Routes
Method	Endpoint	Description	Requires Auth
POST	/register	Register a new user	❌
POST	/token	Obtain a JWT access token	❌
👤 User Routes
Method	Endpoint	Description	Requires Auth
GET	/user/posts	Get all posts by the logged-in user	✅
📝 Post Routes
Method	Endpoint	Description	Requires Auth
GET	/posts	Get all posts (rate limited)	❌
GET	/search/posts	Search posts by title or content	❌
DELETE	/posts/{id}	Soft-delete a post by its ID	✅
🗂️ Project Structure
plaintext
Copy code
.
├── app
│   ├── __init__.py
│   ├── main.py       # Entry point for the application
│   ├── models.py     # SQLAlchemy models for database tables
│   ├── schemas.py    # Pydantic models for data validation
│   ├── crud.py       # CRUD operations for database interaction
│   ├── database.py   # Database configuration
│   └── auth.py       # Authentication and JWT utilities
├── requirements.txt  # Required Python libraries
└── .gitignore        # Ignored files
🎯 Learning Goals
I created this project to:

Practice CRUD operations with a relational database.
Understand API development using FastAPI.
Explore JWT-based authentication.
Learn rate limiting and middleware in API design.
Apply Python tools like SQLAlchemy and Pydantic

📜 License
This project is licensed under the MIT License. You are free to use, modify, and distribute it as per the terms of the license.

Feel free to explore the app, contribute to its development, or use it as a learning tool. If you have any suggestions or questions, feel free to reach out!

css
Copy code

This **README.md** file provides a detailed overview of your project, from features to setup
