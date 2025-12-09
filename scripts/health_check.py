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
from urllib import error, request


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


def load_env_vars(env_path: Path) -> dict:
    """
    Простейший парсер .env:
    - интересуемся только PUBLIC_HTTP_PORT для HTTP-проверки Nginx.
    - игнорируем пустые строки и комментарии.
    Возвращаем словарь переменных, если файл найден и корректен.
    """
    values: dict = {}

    if not env_path.is_file():
        return values

    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            values[key.strip()] = val.strip()

    return values


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


def check_http_endpoint(url: str) -> bool:
    """
    Делает быстрый HTTP-запрос к Nginx.
    Возвращает True, если ответ с кодом < 400.
    Любая ошибка соединения/HTTP приведёт к False, но не оборвёт выполнение.
    """

    try:
        with request.urlopen(url, timeout=5) as response:
            return response.status < 400
    except error.HTTPError as http_err:
        print(
            f"[WARN] HTTP {http_err.code} от {url}. "
            "Проверь, что Nginx и Wiki.js подняты и отдают контент.",
            file=sys.stderr,
        )
    except error.URLError as url_err:
        print(
            f"[WARN] Не удалось подключиться к {url}: {url_err.reason}. "
            "Проверь docker compose up и порты.",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"[WARN] Неожиданная ошибка при HTTP-проверке {url}: {e}",
            file=sys.stderr,
        )

    return False


def main() -> int:
    status_counters = {"OK": 0, "WARN": 0, "ERROR": 0}

    def log(level: str, message: str) -> None:
        """
        Упрощённый логгер, чтобы в конце показать сводку статусов.
        INFO считаем информацией, а OK/WARN/ERROR учитываем в подсчёте.
        """

        target = sys.stderr if level in ("ERROR", "WARN") else sys.stdout
        print(f"[{level}] {message}", file=target)
        if level in status_counters:
            status_counters[level] += 1

    # Проверяем права администратора / root
    if not is_admin():
        log("ERROR", "Скрипт должен выполняться от имени администратора.")
        if os.name == "nt":
            log(
                "WARN",
                "Запусти терминал (PowerShell / CMD) 'От имени администратора' и повтори.",
            )
        else:
            log("WARN", "Запусти: sudo python scripts/health_check.py")
        return 1

    print("=== Health-check viking-rise-wiki-infra ===")
    log("INFO", f"OS: {platform.system()} {platform.release()}")

    # Корень проекта — две директории выше относительно текущего файла
    root_dir = Path(__file__).resolve().parents[1]
    log("INFO", f"Корень проекта: {root_dir}")

    # Проверяем наличие docker-compose.yml
    compose_file = root_dir / "docker-compose.yml"
    if not compose_file.is_file():
        log("ERROR", "Не найден docker-compose.yml в корне проекта.")
        return 1
    log("OK", "Найден docker-compose.yml")

    # Проверяем .env (не обязательно, но полезно)
    env_file = root_dir / ".env"
    env_vars = load_env_vars(env_file)

    if not env_file.is_file():
        log("WARN", "Файл .env не найден.")
        log("WARN", "Создай его из .env.example и заполни своими значениями.")
    else:
        log("OK", "Найден .env")

    # Проверяем/создаём папки data/db и data/wiki
    db_dir = root_dir / "data" / "db"
    wiki_dir = root_dir / "data" / "wiki"

    for folder in (db_dir, wiki_dir):
        if not folder.exists():
            log("WARN", f"Папка {folder} отсутствует, создаю...")
            try:
                folder.mkdir(parents=True, exist_ok=True)
                log("OK", f"Папка {folder} создана.")
            except Exception as e:
                log("ERROR", f"Не удалось создать папку {folder}: {e}")
                return 1
        else:
            log("OK", f"Папка {folder} существует.")

    # Определяем команду для compose
    try:
        compose_cmd = find_compose_command()
        log("OK", f"Используем команду для compose: {' '.join(compose_cmd)}")
    except RuntimeError as e:
        log("ERROR", str(e))
        return 1

    # Показываем статус контейнеров (docker compose ps)
    try:
        log("INFO", "Проверяю статус контейнеров (docker compose ps)...")
        ps_result = subprocess.run(
            [*compose_cmd, "ps"],
            cwd=root_dir,
            text=True,
        )
        if ps_result.returncode != 0:
            log(
                "WARN",
                "Команда docker compose ps завершилась с ошибкой. "
                "Убедись, что Docker запущен и compose-файл корректный.",
            )
    except FileNotFoundError as e:
        log("ERROR", f"Не удалось выполнить docker compose ps: {e}")
        return 1
    except Exception as e:
        log("ERROR", f"Неожиданная ошибка при проверке docker compose ps: {e}")
        return 1

    # HTTP-проверка Nginx, чтобы убедиться, что Wiki.js доступен снаружи контейнеров
    public_port = env_vars.get("PUBLIC_HTTP_PORT", "80")
    target_url = f"http://localhost:{public_port}"
    log(
        "INFO",
        "Пробую HTTP-запрос к Nginx (ожидается 200/302). "
        f"URL: {target_url}",
    )

    if check_http_endpoint(target_url):
        log("OK", "Nginx отвечает на внешний порт. Wiki.js должен быть доступен.")
    else:
        log(
            "WARN",
            "HTTP-проверка не подтвердила доступность Nginx. "
            "Убедись, что контейнеры запущены и PUBLIC_HTTP_PORT открыт.",
        )

    log("INFO", "Если контейнеры не запущены, выполни: docker compose up -d")

    if status_counters["ERROR"]:
        log(
            "ERROR",
            "Проверка завершилась с ошибками. Исправь их и повтори запуск скрипта.",
        )
        return 1

    log("OK", "Проверки завершены. Критических ошибок не обнаружено.")
    log(
        "INFO",
        "Сводка: "
        f"OK={status_counters['OK']}, "
        f"WARN={status_counters['WARN']}, "
        f"ERROR={status_counters['ERROR']}",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
