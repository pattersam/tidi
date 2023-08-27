import logging
import os

import tidi

logging.basicConfig(level=logging.INFO)


def load_db_conn_string() -> str:
    return os.environ.get("DB_CONN_STRING", "db://demo-db")


@tidi.inject
class Fridge:
    def __init__(self, db_conn_string: tidi.Injected[str] = tidi.Provider(load_db_conn_string)):
        self.db_conn_string = db_conn_string

    def get_snack(self):
        print(f"getting snack from {self.db_conn_string}")


def main():
    fridge = Fridge()
    fridge.get_snack()


if __name__ == "__main__":
    main()
