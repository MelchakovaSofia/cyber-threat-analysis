# Архітектура системи

## Загальна схема

```
[Frontend: Bootstrap 5]
        |  HTTPS / REST + JWT
[FastAPI backend]
   |          |            |
   |          |            +-- [ML-модуль: scikit-learn, joblib]
   |          +-- [Сервіси: імпорт, аналіз, сповіщення]
   +-- [PostgreSQL: users, network_logs, threats, ml_models, alerts]
```

## Потік даних

1. **Збір.** Користувач завантажує журнал (CSV/JSON) → `services/log_import.py`
   перевіряє колонки, чистить дублікати й некоректні значення → `network_logs`.
2. **Формування ознак.** `ml/features.py` будує ознаки: порт, обсяг трафіку,
   година активності, код протоколу, ознака невдалого входу, кількість запитів з IP.
3. **Навчання.** `ml/trainer.py` навчає модель (Random Forest, Decision Tree,
   Logistic Regression) або будує модель аномалій (Isolation Forest, K-Means),
   зберігає її через joblib і записує метрики в `ml_models`.
4. **Аналіз.** `ml/predictor.py` рахує ймовірність загрози для кожного запису,
   `services/analysis.py` додатково застосовує евристичні правила
   (brute force, flood) і зберігає результати в `threats`.
5. **Сповіщення.** `services/alerts.py` формує попередження для загроз рівня
   high/critical і зберігає їх у `alerts`.
6. **Відображення.** Dashboard отримує агреговану статистику
   через `GET /api/analysis/stats`.

## Ролі

- **Адміністратор** — навчання та активація моделей, повний доступ.
- **Аналітик** — перегляд логів, запуск аналізу, робота з попередженнями.

## Схема бази даних

- `users` (id, login, email, password, role, created_at)
- `network_logs` (id, ip_address, timestamp, protocol, port, bytes_sent, bytes_received, status)
- `threats` (id, log_id → network_logs, threat_type, probability, severity, description, created_at)
- `ml_models` (id, model_name, version, accuracy, path, is_active, created_at)
- `alerts` (id, threat_id → threats, message, level, status, created_at)
