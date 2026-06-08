# ThreadBase

A RESTful forum API where users sign up, publish posts, and vote on others - built with FastAPI and PostgreSQL.

---

## Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy with Alembic migrations
* **Auth:** OAuth2 password flow, JWT bearer tokens, bcrypt hashing via Passlib
* **Testing:** Pytest with a dedicated test database and fixtures
* **CI/CD:** GitHub Actions (test, build, deploy)
* **Deployment:** Heroku (live) · Docker Hub image available

---

## Features

* User registration and login with bcrypt-hashed passwords
* JWT authentication with OAuth2 password flow
* Full post CRUD: create, read, update, and delete, with ownership enforcement
* Voting system: upvote or remove a vote per post per user
* Search posts by title, with configurable pagination and offset
* Normalised 3-table PostgreSQL schema (users, posts, votes) with foreign-key constraints and cascading deletes
* Dockerised with separate dev and prod Compose configurations
* Automated database migrations on deploy via Alembic release phase
* Automated test, build, and deploy pipeline via GitHub Actions

---

## API

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/users/` | No | Register a new user |
| `GET` | `/users/{id}` | No | Get user by ID |
| `POST` | `/login` | No | Login, returns JWT token |
| `GET` | `/posts/` | No | List posts with search, limit, and skip |
| `POST` | `/posts/` | Yes | Create a post |
| `GET` | `/posts/{id}` | No | Get post by ID |
| `PUT` | `/posts/{id}` | Yes | Update a post (owner only) |
| `DELETE` | `/posts/{id}` | Yes | Delete a post (owner only) |
| `POST` | `/vote/` | Yes | Upvote or remove a vote on a post |

Interactive docs (live): `https://threadbase-d8a4ccf7145c.herokuapp.com/docs`

---

## Getting Started

### Prerequisites

* Python 3.12+
* PostgreSQL
* Docker and Docker Compose (optional)

---

### Local Setup

1. Clone the repository

```
git clone https://github.com/jakeoreillyy/threadbase.git
cd threadbase
```

2. Create and activate a virtual environment

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=<your_database_name>
DATABASE_USERNAME=<your_username>
DATABASE_PASSWORD=<your_password>
SECRET_KEY=<your_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

To generate a secure `SECRET_KEY`:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

5. Run migrations

```
alembic upgrade head
```

6. Start the server

```
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

---

### Docker Setup

**Option A: Pull the pre-built image from Docker Hub**

```
docker pull jakeoreilly/threadbase
```

**Option B: Build and run the full stack locally**

1. Create a `.env.docker` file in the project root - same variables as `.env` but with `DATABASE_HOSTNAME=postgres`:

```env
DATABASE_HOSTNAME=postgres
DATABASE_PORT=5432
DATABASE_NAME=<your_database_name>
DATABASE_USERNAME=<your_username>
DATABASE_PASSWORD=<your_password>
SECRET_KEY=<your_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

2. Start the full stack (dev - includes auto reload and a volume mount)

```
docker-compose -f docker-compose-dev.yml up -d
```

3. Run migrations

```
docker-compose -f docker-compose-dev.yml exec api alembic upgrade head
```

For a production-like environment (no volume mount, no `--reload`), use `docker-compose-prod.yml` instead.

---

## Testing

The test suite uses pytest with a dedicated test database, spun up fresh for each test function so cases run in isolation. Fixtures handle user creation, token generation, an authorised client, and seed posts.

Coverage spans all four routers - authentication, users, posts, and votes, including:

* User registration and login, with parameterised invalid-credential cases
* JWT issuing and decoding on login
* Post CRUD with ownership enforcement (403 on editing or deleting another user's post)
* Unauthorised access returning 401 across protected routes
* Voting, duplicate-vote conflicts (409), and removing votes
* 404 handling for non-existent posts and votes

Set up a test database named `<your_database_name>_test`, then run:

```
pytest -v -s
```

---

## CI/CD

A GitHub Actions pipeline (`.github/workflows/build-deploy.yml`) runs automatically on every push and pull request to `main`:

1. **Test** - spins up a Postgres service container, installs dependencies, and runs the full pytest suite against a fresh test database
2. **Build** - builds the Docker image and pushes it to Docker Hub (only after tests pass)
3. **Deploy** - releases the new build to Heroku, where Alembic migrations run automatically via the `release` phase in the `Procfile`

Deployment only proceeds if the test and build stages succeed, so broken code never reaches production.
