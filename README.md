## Litestar Auth

### 1. Prerequisites

* Python 3.13+
* [Poetry](https://python-poetry.org/) (dependency manager)

Poetry installation (if you don't have it):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Environment variables (.env)

Copy the `.env.example` file to `.env` and change the values as needed:

```bash
cp .env.example .env
```

### 3. Install dependencies

```bash
poetry install
```

Install the shell plugin and activate the virtual shell:

```bash
poetry self add poetry-plugin-shell
poetry shell
```

Configure pre-commit hooks:

```bash
pre-commit install --config pre-commit.yaml
```

### 4. Database

Create the database (adjust the name according to your DSN):

```bash
createdb db
```

Apply manual SQL migrations (e.g.: content in `src/db/migrations/`).

### 5. Run the server

Basic command:

```bash
litestar run
```

Examples with options:

```bash
litestar run -r -P -d -p 9000 -H 0.0.0.0
litestar run --wc 4
litestar run -h
```

### 6. OpenAPI / ReDoc

Access at:

```
http://localhost:PORT/schema/redoc
```

Replace `PORT` with the port used (default 8000 if not specified).

Extra plugin for Poetry

```bash
poetry self add poetry-plugin-up
poetry up --latest
```

---

**More features:** [litestar-asyncpg](https://github.com/YuriFontella/litestar-asyncpg)
