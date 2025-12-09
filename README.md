# viking-rise-wiki-infra

Инфраструктура для wiki-сайта по игре **Viking Rise** на базе **Wiki.js**.

> Этот репозиторий отвечает **только за инфраструктуру** (Docker, БД, Nginx, скрипты), а не за контент самой wiki.

---

## Цели проекта

- Развернуть **Wiki.js** с PostgreSQL и Nginx.
- Обеспечить удобный и стабильный запуск на **Windows (через Docker Desktop)** и на Linux/WSL.
- Добавить полезные скрипты:
  - health-check инфраструктуры,
  - резервное копирование БД.
- Подготовить основу для дальнейшей настройки:
  - цветовая схема и стили под Viking Rise,
  - места под рекламные баннеры,
  - документация по структуре контента и ролям редакторов.

---

## Технологии

- **Docker + Docker Compose**
- **PostgreSQL 15 (alpine)**
- **Wiki.js v2**
- **Nginx (alpine)**
- **Python 3** (служебные скрипты)
- ОС: основная рабочая среда — **Windows + Docker Desktop**, с прицелом на совместимость с Linux/WSL.

---

## Документация

- [Базовая настройка Wiki.js через веб-интерфейс](docs/wiki-setup.md)

---

## Структура репозитория (основное)

```text
viking-rise-wiki-infra/
├─ README.md                 # Общее описание проекта
├─ AGENTS.md                 # Инструкции для ИИ-агентов (Codex и др.)
├─ .gitignore                # Исключения из Git
├─ .env.example              # Пример переменных окружения (реальный .env не коммитим)
├─ docker-compose.yml        # Запуск Wiki.js + PostgreSQL + Nginx
├─ nginx/
│  ├─ nginx.conf             # Базовый конфиг Nginx
│  └─ conf.d/
│     └─ wiki.conf           # Виртуальный хост для Wiki.js
├─ scripts/
│  ├─ health_check.py        # Health-check инфраструктуры (Python)
│  └─ backup_db.py           # Резервное копирование БД (Python)
├─ docs/
│  └─ wiki-setup.md          # Пошаговая настройка Wiki.js через веб-интерфейс
├─ backups/                  # Сюда складываются дампы БД (игнорируется Git)
└─ data/
   ├─ db/                    # Данные PostgreSQL (volume, в Git не входит)
   └─ wiki/                  # Данные Wiki.js (volume, в Git не входит)

---

## Перед началом

**Требования:**

- Docker Desktop (Windows) или Docker Engine (Linux/WSL) с поддержкой Docker Compose v2.
- Python 3.10+ (для служебных скриптов). Можно использовать системный `python`/`py`.
- Права администратора (Windows) или `sudo` (Linux/WSL), чтобы обращаться к Docker и создавать служебные каталоги.

---

## Пошаговый запуск (Windows / WSL / Linux)

1. **Подготовить переменные окружения**
   - Скопируйте `.env.example` → `.env`.
   - Укажите свои значения: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `PUBLIC_HTTP_PORT`.
   - На Windows можно использовать PowerShell: `Copy-Item .env.example .env`.
2. **Запустить инфраструктуру**
   - Выполните `docker compose up -d` из корня репозитория.
   - При первом запуске будут созданы каталоги `data/db` и `data/wiki` для volume-данных.
3. **Проверить окружение скриптом health-check**
   - Linux/WSL: `sudo python scripts/health_check.py`
   - Windows: запустите PowerShell/Command Prompt «От имени администратора» и выполните `py scripts\health_check.py`.
   - Скрипт убедится, что Docker доступен, `.env` найден, а каталоги `data/` созданы.
4. **Создать резервную копию БД (после инициализации Wiki.js)**
   - Linux/WSL: `sudo python scripts/backup_db.py`
   - Windows (администратор): `py scripts\backup_db.py`
   - Дамп сохраняется в `backups/wikijs_db_YYYYMMDD_HHMMSS.sql` (папка игнорируется Git).
5. **Открыть Wiki.js**
   - По умолчанию: `http://localhost:<PUBLIC_HTTP_PORT>` из `.env` (например, `http://localhost:8080`).
   - Первоначальная настройка admin-аккаунта выполняется через веб-интерфейс Wiki.js.
6. **Остановить/перезапустить**
   - Остановить: `docker compose down`
   - Перезапустить после изменения конфигов: `docker compose up -d --force-recreate`

> Скрипты проверяют права и выводят понятные сообщения на русском. Если Docker или Compose недоступны, сначала исправьте окружение, затем повторите запуск.

---

## Состав сервисов docker-compose

- **db** — PostgreSQL 15 (alpine). Данные хранятся в `./data/db`. Health-check использует `pg_isready`.
- **wiki** — Wiki.js v2. Использует БД `db` и хранит загрузки в `./data/wiki`. Health-check — HTTP-запрос к приложению.
- **nginx** — reverse-proxy, публикует порт из переменной `PUBLIC_HTTP_PORT`. Конфигурация лежит в `nginx/`.

> Все чувствительные данные берутся из `.env`; сам файл в Git не коммитим.
