from __future__ import annotations

from app.models.database import init_db, seed_default_catalog


def main() -> None:
    init_db()
    seed_default_catalog()
    print("Database seeded successfully.")


if __name__ == "__main__":
    main()
