# Інтелектуальна система аналізу кіберзагроз

Дипломний проєкт (STEP Computer Academy). Веборієнтована система для моніторингу
мережевої активності, збору й аналізу журналів подій та виявлення підозрілої
поведінки за допомогою машинного навчання.

**Статус:** робочий прототип (backend API, ML, вебінтерфейс, Docker, Kubernetes-маніфести, тести).

## Стек

| Рівень   | Технології |
|----------|------------|
| Backend  | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| БД       | PostgreSQL 16 |
| ML       | scikit-learn, pandas, NumPy, joblib |
| Frontend | HTML/CSS/JS, Bootstrap 5 |
| DevOps   | Docker, Docker Compose, Kubernetes, Azure, GitHub Actions |

## Структура

```
backend/app/
    api/        REST-ендпоїнти (auth, logs, analysis, ml, alerts)
    models/     ORM-моделі (Users, NetworkLogs, Threats, MLModels, Alerts)
    schemas/    Pydantic-схеми
    services/   імпорт логів, аналіз активності, генерація сповіщень
    ml/         формування ознак, навчання, прогнозування
    database/   підключення та сесії
    auth/       JWT, хешування паролів, ролі
    utils/      допоміжні утиліти
frontend/       вхід, dashboard, логи, сповіщення, моделі, профіль, налаштування
docker/         Dockerfile
kubernetes/     Deployment, Service, ConfigMap, Secret, Ingress
docs/           документація, тестовий набір даних
tests/          pytest (auth, API, ML)
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up --build
```

- API та Swagger: http://localhost:8000/docs
- Frontend: http://localhost:8080

## Локальний запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd backend && uvicorn app.main:app --reload
```

## Тести

```bash
DATABASE_URL="sqlite:///./test.db" SECRET_KEY=test pytest -q
```

## Сценарій демонстрації

1. `POST /api/auth/register` — створити користувача з роллю `admin`.
2. `POST /api/auth/login` — отримати access/refresh токени.
3. `POST /api/logs/import` — завантажити `docs/sample_logs.csv`.
4. `POST /api/ml/train` — навчити модель (`random_forest`), отримати метрики.
5. `POST /api/analysis/run` — запустити аналіз, отримати загрози й сповіщення.
6. `GET /api/analysis/stats` — статистика для dashboard.

## REST API

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/api/auth/register` | реєстрація |
| POST | `/api/auth/login` | авторизація (JWT) |
| POST | `/api/auth/refresh` | оновлення токена |
| GET  | `/api/auth/me` | поточний користувач |
| GET/POST/DELETE | `/api/logs` | перегляд, додавання, видалення логів |
| POST | `/api/logs/import` | імпорт CSV / JSON |
| POST | `/api/analysis/run` | запуск аналізу |
| GET  | `/api/analysis/results` | результати аналізу |
| GET  | `/api/analysis/results/{id}` | деталі інциденту |
| GET  | `/api/analysis/stats` | статистика dashboard |
| POST | `/api/ml/train` | навчання моделі (тільки admin) |
| GET  | `/api/ml/models` | список моделей |
| POST | `/api/ml/models/{id}/activate` | активація моделі |
| POST | `/api/ml/predict` | прогноз |
| GET/PATCH | `/api/alerts` | журнал попереджень |

## Документація

- [Архітектура](docs/architecture.md)
- [Керівництво користувача](docs/user-guide.md)
- [Розгортання в Azure](docs/deployment.md)
- Swagger: `/docs`

## Що лишається поза локальним прототипом

- фактичне розгортання в підписці Azure (AKS + Azure Database for PostgreSQL + ACR + Azure Monitor);
  інструкція є в `docs/deployment.md`
