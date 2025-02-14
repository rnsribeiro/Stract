from flask import Flask
import os
from routes import register_routes

app = Flask(__name__)

# Registrar rotas separadamente
register_routes(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Porta padrão 5000
    app.run(host="0.0.0.0", port=port, debug=True)
