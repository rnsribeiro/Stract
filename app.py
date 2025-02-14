from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def root():
    """Endpoint raiz com informações pessoais"""
    user_data = {
        "name": "Rodrigo Nunes Sampaio Ribeiro",
        "email": "rnsribeiro@gmail.com",
        "linkedin": "https://www.linkedin.com/in/rodrigo-nsribeiro/"
    }
    return render_template('index.html', user_data=user_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))  # Define a porta como 80
    app.run(host="0.0.0.0", port=port, debug=True)
