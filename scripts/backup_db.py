#!/usr/bin/env python
# scripts/backup_db.py
# Скрипт резервного копирования БД Wiki.js (PostgreSQL) в локальный файл.
#
# Что делает:
#  - Проверяет запуск от имени администратора.
#  - Читает .env и вытаскивает POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.
#  - Создаёт папку backups/ в корне проекта.
#  - Вызывает pg_dump внутри контейнера db через docker compose exec -T.
#  - Сохраняет дамп в файл вида wikijs_db_YYYYMMDD_HHMMSS.sql.
#  - Ведёт логи в консоль и logs/backup.log, удаляя старые записи по мере ротации.
#
# Лог выводится в консоль и в файл logs/backup.log.

import logging
import os
import sys
import subprocess
from pathlib import Path
import shutil
from datetime import datetime
import platform


def is_admin() -> bool:
    """Та же проверка прав, что и в health_check.py."""
    try:
        if os.name == "nt":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return hasattr(os, "geteuid") and os.geteuid() == 0
    except Exception:
        return False


def find_compose_command() -> list:
    """Определяем команду для docker compose (v2 или v1)."""
    docker_path = shutil.which("docker")
    if docker_path is None:
        raise RuntimeError("Docker не найден в PATH. Установи Docker Desktop и попробуй снова.")

    # Пробуем docker compose (v2)
    try:
        result = subprocess.run(
            [docker_path, "compose", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            return [docker_path, "compose"]
    except Exception:
        pass

    # Пробуем docker-compose (v1)
    compose_v1_path = shutil.which("docker-compose")
    if compose_v1_path is not None:
        return [compose_v1_path]

    raise RuntimeError(
        "Не найден ни 'docker compose', ни 'docker-compose'. "
        "Установи Docker Compose и повтори попытку."
    )


def load_env_vars(env_path: Path) -> dict:
    """
    Простейший парсер .env:
    берем строки вида KEY=VALUE без пробелов.
    Нас интересуют только:
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB
    """
    required_keys = {"POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"}
    values: dict = {}

    if not env_path.is_file():
        raise FileNotFoundError(f"Файл .env не найден по пути: {env_path}")

    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if key in required_keys:
                values[key] = val

    missing = required_keys - set(values.keys())
    if missing:
        raise ValueError(f"В .env отсутствуют необходимые переменные: {', '.join(missing)}")

    return values


def setup_logger(log_dir: Path) -> logging.Logger:
    """
    Готовим логгер с выводом в консоль и файл logs/backup.log.
    Логи помогают отследить успешные и неуспешные попытки бэкапа.
    """

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "backup.log"

    logger = logging.getLogger("backup_db")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def rotate_backups(backups_dir: Path, keep_last: int, logger: logging.Logger) -> None:
    """
    Простая ротация: оставляем только keep_last свежих бэкапов.
    Остальные аккуратно удаляем с логированием, чтобы не копить гигабайты.
    """

    backup_files = sorted(
        backups_dir.glob("wikijs_db_*.sql"),
        key=lambda file_path: file_path.stat().st_mtime,
        reverse=True,
    )

    if len(backup_files) <= keep_last:
        return

    for obsolete_file in backup_files[keep_last:]:
        try:
            obsolete_file.unlink()
            logger.info("Удалён старый бэкап: %s", obsolete_file)
        except Exception as e:
            logger.warning("Не удалось удалить %s: %s", obsolete_file, e)


def main() -> int:
    # Проверка прав
    if not is_admin():
        print("[ERROR] Скрипт должен выполняться от имени администратора.", file=sys.stderr)
        if os.name == "nt":
            print("        Запусти терминал (PowerShell / CMD) 'От имени администратора' и повтори.", file=sys.stderr)
        else:
            print("        Запусти: sudo python scripts/backup_db.py", file=sys.stderr)
        return 1

    root_dir = Path(__file__).resolve().parents[1]
    logger = setup_logger(root_dir / "logs")

    logger.info("=== Резервное копирование БД Wiki.js ===")
    logger.info("OS: %s %s", platform.system(), platform.release())
    logger.info("Корень проекта: %s", root_dir)

    env_path = root_dir / ".env"
    try:
        env_vars = load_env_vars(env_path)
    except (FileNotFoundError, ValueError) as e:
        logger.error("%s", e)
        return 1

    postgres_user = env_vars["POSTGRES_USER"]
    postgres_db = env_vars["POSTGRES_DB"]

    # Папка для бэкапов
    backups_dir = root_dir / "backups"
    try:
        backups_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Папка для бэкапов: %s", backups_dir)
    except Exception as e:
        logger.error("Не удалось создать папку для бэкапов: %s", e)
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backups_dir / f"wikijs_db_{timestamp}.sql"
    logger.info("Файл бэкапа: %s", backup_file)

    # Ищем docker compose / docker-compose
    try:
        compose_cmd = find_compose_command()
        logger.info("Используем команду для compose: %s", " ".join(compose_cmd))
    except RuntimeError as e:
        logger.error("%s", e)
        return 1

    # Команда pg_dump внутри контейнера db:
    # docker compose exec -T db pg_dump -U <user> <db>
    cmd = [*compose_cmd, "exec", "-T", "db", "pg_dump", "-U", postgres_user, postgres_db]

    try:
        with backup_file.open("w", encoding="utf-8") as f:
            proc = subprocess.run(
                cmd,
                cwd=root_dir,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
            )
    except FileNotFoundError as e:
        logger.error("Не удалось запустить docker compose: %s", e)
        return 1
    except Exception as e:
        logger.error("Неожиданная ошибка при выполнении pg_dump: %s", e)
        return 1

    if proc.returncode != 0:
        # Если pg_dump отдал ошибку — удаляем пустой/битый файл и выводим stderr
        try:
            if backup_file.exists():
                backup_file.unlink()
        except Exception:
            pass

        logger.error("pg_dump завершился с ошибкой")
        if proc.stderr:
            logger.error(proc.stderr)
        logger.info(
            "Убедись, что контейнер 'db' запущен и переменные окружения указаны корректно."
        )
        return 1

    logger.info("Бэкап успешно создан.")

    # Простая ротация, по умолчанию оставляем 10 последних бэкапов
    rotate_backups(backups_dir, keep_last=10, logger=logger)

    logger.info("Можно скопировать файл из папки backups/ для хранения вне сервера.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
