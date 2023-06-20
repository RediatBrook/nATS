from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return 'About'

# Implement adding a job to the database
@app.route('/jobs/add/<description>')
def add_job(description):
    return description

# Implement adding a resume to a job
@app.route('/jobs/<int:id>/submit')
def submit_resume(id):
    return id