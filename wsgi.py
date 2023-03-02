import sys
import os
print(sys.path)

# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(basedir, '..')))

# Import the Flask application instance
from project import create_app


# Create the WSGI application object
application = create_app()

# If running under Gunicorn, set the number of worker processes
if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
    application.config['WORKERS'] = int(os.environ.get('WEB_CONCURRENCY', 1))

if __name__ == '__main__':
    application.run()
   
