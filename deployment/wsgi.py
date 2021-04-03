from app import app
import os

os.environ['FLASK_ENV'] = "production"

if __name__ == "__main__":
  app.run()