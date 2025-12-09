# viking-rise-wiki-infra

Инфраструктура для Wiki-сайта по игре **Viking Rise** на базе **Wiki.js**.

## Состав

- `docker-compose.yml` — запуск Wiki.js + PostgreSQL + Nginx.
- `.env.example` — пример настроек окружения. Реальный `.env` **не коммитим**.
- `nginx/` — конфигурация Nginx, который проксирует трафик к Wiki.js.
- `data/` — данные БД и Wiki.js (volumes).
- `scripts/health_check.sh` — health-check инфраструктуры.
- `scripts/backup_db.sh` — резервное копирование БД.

## Быстрый старт

1. Клонировать репозиторий:

   ```bash
   git clone <url> viking-rise-wiki-infra
   cd viking-rise-wiki-infra
