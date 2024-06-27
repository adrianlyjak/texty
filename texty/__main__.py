from texty import database
from texty.cli import run_scenario


if __name__ == "__main__":
    try:
        database.init_db()
        run_scenario("llama70b-5")
    except KeyboardInterrupt:
        print("Interrupted...")
