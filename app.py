from flask import Flask, render_template
import os
import openai

app = Flask(__name__)

openai_api_key = os.getenv('OPENAI_API_KEY')
flask_secret_key = os.getenv('FLASK_SECRET_KEY')
app.secret_key = flask_secret_key
openai.api_key = openai_api_key

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)