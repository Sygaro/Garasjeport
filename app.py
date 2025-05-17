# ==========================================
# Filnavn: app.py
# Starter Flask-app og registrerer Blueprints
# ==========================================

from flask import Flask
from routes.port_routes import port_routes
from routes.status_routes import status_routes
from routes.config_routes import config_routes


app = Flask(__name__)
app.register_blueprint(port_routes)
app.register_blueprint(status_routes)
app.register_blueprint(config_routes)

@app.route("/")
def index():
    return "<h3>Garage API er aktiv (modulær versjon)</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
