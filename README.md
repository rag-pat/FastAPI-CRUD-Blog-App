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
