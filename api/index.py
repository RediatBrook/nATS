from flask import Flask
from flask import send_file
app = Flask(__name__)

@app.route('/')
def home():
    return send_file('./frontend/index.html')

@app.route('/about')
def about():
    return 'About'

# Implement Adding a Job to the Database
@app.route('/jobs/add')
def add_job():
    return 'Add Job'

#implement A Resume to 
@app.route('/jobs/<int:id>/submit')
def submit_resume(id):
    return str(id)