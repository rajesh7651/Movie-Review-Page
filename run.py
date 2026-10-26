from app import app, create_database
from waitress import serve

create_database()

serve(app, host="127.0.0.1", port=5000)