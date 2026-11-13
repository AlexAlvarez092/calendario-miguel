import logging

from .config import load_settings
from .telegram_app import build_application


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # its URLs contain the bot token
    build_application(load_settings()).run_polling()


if __name__ == "__main__":
    main()
