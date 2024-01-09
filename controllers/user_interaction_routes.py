from flask import render_template

def index():
  return render_template('index.html')

def query():
  return render_template('query.html')

def upload_screen():
  return render_template('upload.html')
