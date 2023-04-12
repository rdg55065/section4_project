from flask import Flask, render_template, request, redirect, url_for
from model import kor_music

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/keyword', methods =['POST', 'GET'])
def keyword():
    if request.method == 'POST':
        word = request.form
        word = str(word['keyword'])
        result = kor_music(word)
        return render_template('keyword.html', result=result), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9900)
