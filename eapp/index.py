from flask import render_template
from eapp import app

@app.route('/')
def index():
    return render_template('index.html', msg='Test123')

if __name__ == '__main__':
    app.run(debug=True)