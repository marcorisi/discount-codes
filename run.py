"""Application entry point."""

import os

from dotenv import load_dotenv

from app import create_app

load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    app.run()
