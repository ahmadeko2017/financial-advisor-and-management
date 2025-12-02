import os
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


def main():
    url = os.getenv("DATABASE_URL")
    if not url or url.startswith("${"):
        print("DATABASE_URL not set or placeholder; using sqlite fallback")
        return

    attempts = 20  # ~40s max
    for i in range(attempts):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is reachable")
            return
        except OperationalError as exc:
            print(f"[wait_for_db] attempt {i+1}/{attempts} failed: {exc}")
            time.sleep(2)
        except Exception as exc:  # fallback for transient issues
            print(f"[wait_for_db] attempt {i+1}/{attempts} unexpected error: {exc}")
            time.sleep(2)
    print("Database not reachable, giving up", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
