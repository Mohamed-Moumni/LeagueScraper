import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s"
)

logger = logging.getLogger(__name__)
