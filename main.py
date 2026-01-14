import logging
from ui import run_cli


class UzbekFormatter(logging.Formatter):
    MAP = {
        "DEBUG": "DEBUG",
        "INFO": "MA'LUMOT",
        "WARNING": "OGOX",
        "ERROR": "XATO",
        "CRITICAL": "JIDDIY",
    }

    def format(self, record):
        orig = record.levelname
        record.levelname = self.MAP.get(orig, orig)
        s = super().format(record)
        record.levelname = orig
        return s


def configure_logging():
    logger = logging.getLogger("educational")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("data.log")
    fh.setLevel(logging.INFO)
    fmt = UzbekFormatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger


def main():
    configure_logging()
    run_cli()


if __name__ == "__main__":
    main()
