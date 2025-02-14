from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def root():
    """Endpoint raiz com informações pessoais"""
    # Dados que você quer exibir na página
    user_data = {
        "name": "Rodrigo Nunes Sampaio Ribeiro",
        "email": "rnsribeiro@gmail.com",
        "linkedin": "https://www.linkedin.com/in/rodrigo-nsribeiro/"
    }

    # Passando os dados para o template
    return render_template('index.html', user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True)
