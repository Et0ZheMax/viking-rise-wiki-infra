#!/usr/bin/env python
# scripts/health_check.py
# Health-check для инфраструктуры viking-rise-wiki-infra.
#
# Что делает:
#  - Проверяет запуск от имени администратора (Windows) или root (Linux).
#  - Проверяет наличие docker и docker compose / docker-compose.
#  - Проверяет наличие docker-compose.yml и .env.
#  - Проверяет/создаёт папки data/db и data/wiki.
#  - Показывает статус контейнеров через docker compose ps.
#
# Лог выводится в консоль.

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil


def is_admin() -> bool:
    """
    Проверка прав администратора:
    - На Windows: через ctypes.windll.shell32.IsUserAnAdmin().
    - На Unix (Linux/WSL): через os.geteuid() == 0.
    """
    try:
        if os.name == "nt":
            import ctypes  # импортируем только при необходимости

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            # На Unix-подобных системах проверяем uid == 0
            return hasattr(os, "geteuid") and os.geteuid() == 0
    except Exception:
        # Если по какой-то причине не удалось проверить — считаем, что не админ
        return False


def find_compose_command() -> list:
    """
    Определяем, какую команду использовать для docker compose:
    - Сначала пробуем `docker compose` (v2).
    - Если не получилось, пробуем `docker-compose` (v1).
    Возвращаем список аргументов для subprocess.run, например:
      ["docker", "compose"] или ["docker-compose"].
    """
    # Проверяем наличие docker
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

    # Если ни один вариант не доступен — ошибку наверх
    raise RuntimeError(
        "Не найден ни 'docker compose', ни 'docker-compose'. "
        "Установи Docker Compose v2 или v1 и повтори попытку."
    )


def main() -> int:
    # Проверяем права администратора / root
    if not is_admin():
        print("[ERROR] Скрипт должен выполняться от имени администратора.", file=sys.stderr)
        if os.name == "nt":
            print("        Запусти терминал (PowerShell / CMD) 'От имени администратора' и повтори.", file=sys.stderr)
        else:
            print("        Запусти: sudo python scripts/health_check.py", file=sys.stderr)
        return 1

    print("=== Health-check viking-rise-wiki-infra ===")
    print(f"[INFO] OS: {platform.system()} {platform.release()}")

    # Корень проекта — две директории выше относительно текущего файла
    root_dir = Path(__file__).resolve().parents[1]
    print(f"[INFO] Корень проекта: {root_dir}")

    # Проверяем наличие docker-compose.yml
    compose_file = root_dir / "docker-compose.yml"
    if not compose_file.is_file():
        print("[ERROR] Не найден docker-compose.yml в корне проекта.", file=sys.stderr)
        return 1
    print("[OK] Найден docker-compose.yml")

    # Проверяем .env (не обязательно, но полезно)
    env_file = root_dir / ".env"
    if not env_file.is_file():
        print("[WARN] Файл .env не найден.")
        print("       Создай его из .env.example и заполни своими значениями.")
    else:
        print("[OK] Найден .env")

    # Проверяем/создаём папки data/db и data/wiki
    db_dir = root_dir / "data" / "db"
    wiki_dir = root_dir / "data" / "wiki"

    for folder in (db_dir, wiki_dir):
        if not folder.exists():
            print(f"[WARN] Папка {folder} отсутствует, создаю...")
            try:
                folder.mkdir(parents=True, exist_ok=True)
                print(f"[OK] Папка {folder} создана.")
            except Exception as e:
                print(f"[ERROR] Не удалось создать папку {folder}: {e}", file=sys.stderr)
                return 1
        else:
            print(f"[OK] Папка {folder} существует.")

    # Определяем команду для compose
    try:
        compose_cmd = find_compose_command()
        print(f"[OK] Используем команду для compose: {' '.join(compose_cmd)}")
    except RuntimeError as e:
