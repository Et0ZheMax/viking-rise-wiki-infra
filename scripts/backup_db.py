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
#
# Лог выводится в консоль.

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


def main() -> int:
    # Проверка прав
    if not is_admin():
        print("[ERROR] Скрипт должен выполняться от имени администратора.", file=sys.stderr)
        if os.name == "nt":
            print("        Запусти терминал (PowerShell / CMD) 'От имени администратора' и повтори.", file=sys.stderr)
        else:
            print("        Запусти: sudo python scripts/backup_db.py", file=sys.stderr)
        return 1

    print("=== Резервное копирование БД Wiki.js ===")
    print(f"[INFO] OS: {platform.system()} {platform.release()}")

    root_dir = Path(__file__).resolve().parents[1]
    print(f"[INFO] Корень проекта: {root_dir}")

    env_path = root_dir / ".env"
    try:
        env_vars = load_env_vars(env_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    postgres_user = env_vars["POSTGRES_USER"]
    postgres_db = env_vars["POSTGRES_DB"]

    # Папка для бэкапов
    backups_dir = root_dir / "backups"
    try:
        backups_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Папка для бэкапов: {backups_dir}")
    except Exception as e:
        print(f"[ERROR] Не удалось создать папку для бэкапов: {e}", file=sys.stderr)
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backups_dir / f"wikijs_db_{timestamp}.sql"
    print(f"[INFO] Файл бэкапа: {backup_file}")

    # Ищем docker compose / docker-compose
    try:
        compose_cmd = find_compose_command()
        print(f"[OK] Используем команду для compose: {' '.join(compose_cmd)}")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
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
        print(f"[ERROR] Не удалось запустить docker compose: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка при выполнении pg_dump: {e}", file=sys.stderr)
        return 1

    if proc.returncode != 0:
        # Если pg_dump отдал ошибку — удаляем пустой/битый файл и выводим stderr
        try:
            if backup_file.exists():
                backup_file.unlink()
        except Exception:
            pass

        print("[ERROR] pg_dump завершился с ошибкой:", file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        print(
            "[INFO] Убедись, что контейнер 'db' запущен и переменные окружения"
            " указаны корректно.",
            file=sys.stderr,
        )
        return 1

    print("[OK] Бэкап успешно создан.")
    print("[INFO] Можно скопировать файл из папки backups/ для хранения вне сервера.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
