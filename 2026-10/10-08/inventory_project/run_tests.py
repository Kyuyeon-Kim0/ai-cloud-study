"""Run integration tests in a disposable MySQL container, never the configured DB."""
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

import mysql.connector


def main():
    password = secrets.token_urlsafe(24)
    environment = os.environ.copy()
    environment.update(MYSQL_DATABASE="inventory_test", MYSQL_USER="test_user",
                       MYSQL_PASSWORD=password, MYSQL_ROOT_PASSWORD=secrets.token_urlsafe(24))
    container = subprocess.check_output([
        "docker", "run", "--rm", "-d", "-p", "127.0.0.1::3306",
        "-e", "MYSQL_DATABASE", "-e", "MYSQL_USER", "-e", "MYSQL_PASSWORD",
        "-e", "MYSQL_ROOT_PASSWORD", "mysql:8.4",
    ], env=environment, text=True).strip()
    try:
        port = subprocess.check_output(["docker", "port", container, "3306"], text=True).strip().rsplit(":", 1)[1]
        deadline = time.monotonic() + 120
        while True:
            try:
                connection = mysql.connector.connect(
                    host="127.0.0.1", port=int(port), user="test_user", password=password,
                    database="inventory_test", connection_timeout=2,
                )
                connection.close()
                break
            except mysql.connector.Error:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Test MySQL did not become ready within 120 seconds.") from None
                time.sleep(2)
        environment.update(MYSQL_HOST="127.0.0.1", MYSQL_PORT=port, INVENTORY_TEST_MODE="1")
        return subprocess.call([sys.executable, "-m", "pytest", "tests", "-q"],
                               cwd=Path(__file__).resolve().parent, env=environment)
    finally:
        subprocess.run(["docker", "rm", "-f", container], stdout=subprocess.DEVNULL, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
