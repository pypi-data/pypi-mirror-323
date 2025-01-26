import logging


def get_logger(name: str, levelname=logging.INFO) -> logging.Logger:
    logging.basicConfig(
        format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s", level=levelname
    )
    logger = logging.getLogger(name=name)

    return logger
