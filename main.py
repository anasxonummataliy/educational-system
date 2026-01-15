import logging
from ui import run_cli


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("data.log", encoding="utf-8"),
        ],
    )
    return logging.getLogger("educational")


def main():
    configure_logging()
    run_cli()


if __name__ == "__main__":
    main()
