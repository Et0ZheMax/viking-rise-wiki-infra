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
└─ data/
   ├─ db/                    # Данные PostgreSQL (volume, в Git не входит)
   └─ wiki/                  # Данные Wiki.js (volume, в Git не входит)
