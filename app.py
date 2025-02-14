import requests
import os
from flask import Flask, render_template
from api_client import get_platforms

app = Flask(__name__)

@app.route('/')
def root():
    """Página inicial com informações pessoais e menu"""
    user_data = {
        "name": "Rodrigo Nunes Sampaio Ribeiro",
        "email": "rnsribeiro@gmail.com",
        "linkedin": "https://www.linkedin.com/in/rodrigo-nsribeiro/"
    }
    return render_template('index.html', user_data=user_data)

@app.route('/plataformas')
def plataformas():
    """Página que exibe uma tabela com as plataformas disponíveis"""
    platforms = get_platforms()
    return render_template('plataformas.html', platforms=platforms)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Mudança para 5000 se porta 80 exigir permissão de root
    app.run(host="0.0.0.0", port=port, debug=True)
