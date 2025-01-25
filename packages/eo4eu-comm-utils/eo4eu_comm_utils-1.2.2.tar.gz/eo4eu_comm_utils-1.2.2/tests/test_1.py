import logging
import logging.config
from eo4eu_comm_utils.format import get_dual_logging_config


if __name__ == "__main__":
    logger = logging.getLogger("test")
    logging.config.dictConfig(get_dual_logging_config(
        "test.log", 0, "INFO"
    ))
    logger.setLevel(logging.INFO)

    logger.info("Hello :D")
