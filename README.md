# Profiles API (Django)

A Django REST Framework API that enriches a name with gender, age, and nationality data, persists it to a database, and exposes CRUD endpoints.

---

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: SQLite (default) — swap to PostgreSQL for production
- **UUID**: UUID v7 via `uuid-extensions`
- **Server**: Gunicorn

---

## Local Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API is available at `http://localhost:8000`

---

## Endpoints

### `POST /api/profiles`
Creates a profile from a name. Returns existing profile if name already exists.

**Request:**
```json
{ "name": "ella" }
```

**Response 201:**
```json
{
  "status": "success",
  "data": {
    "id": "...",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "DRC",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```

**Response 200 (duplicate):**
```json
{
  "status": "success",
  "message": "Profile already exists",
  "data": { ... }
}
```

### `GET /api/profiles`
Returns all profiles. Supports case-insensitive query filters:
- `?gender=male`
- `?country_id=NG`
- `?age_group=adult`

Can be combined: `?gender=male&country_id=NG`

### `GET /api/profiles/<id>`
Returns a single profile by UUID.

### `DELETE /api/profiles/<id>`
Deletes a profile. Returns `204 No Content`.

---

## Age Group Classification

| Age   | Group     |
|-------|-----------|
| 0–12  | child     |
| 13–19 | teenager  |
| 20–59 | adult     |
| 60+   | senior    |

---

## Error Format

```json
{ "status": "error", "message": "<reason>" }
```

| Code | Reason                              |
|------|-------------------------------------|
| 400  | Missing or empty name               |
| 404  | Profile not found                   |
| 422  | Invalid type                        |
| 502  | External API returned invalid data  |

---

## Deployment on Railway

1. Push repo to GitHub
2. New Railway project → Deploy from GitHub
3. Railway detects Python and runs the `Procfile`:
   - `release`: runs `python manage.py migrate`
   - `web`: starts Gunicorn
4. Set environment variables:
   - `SECRET_KEY` — a long random string
   - `PORT` — Railway injects this automatically

### Optional: PostgreSQL on Railway
1. Add a PostgreSQL service in Railway
2. Install `psycopg2-binary` and add to `requirements.txt`
3. Update `DATABASES` in `core/settings.py`:

```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}
```

4. Add `DATABASE_URL` env variable (Railway provides this automatically when you link the service).
