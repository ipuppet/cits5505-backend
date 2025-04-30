from flask import render_template
from myapp import app

@app.route('/')
@app.route('/index')
def index_bp():
    return render_template('index.html')

@app.route('/introductory')
def introductory():
    return render_template('introductory.html')

@app.route('/uploaddata')
def uploaddata():
    return render_template('uploaddata.html')

@app.route('/visualize')
def visualize():
    return render_template('visualize.html')

@app.route('/share')
def share():
    return render_template('share.html')


