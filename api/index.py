from flask import Flask
from flask import render_template
from flask import send_file, request
import os 
import boto3 
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

@app.route("/uploadToS3/")
def uploadToS3():
    text = request.args.get("text")
    bucket_name = 'textfiledata'
    person = str(request.args.get("person"))
    key = 'testingfolder/' + person + '.txt'

    # Create an S3 client using the system variables
    session = boto3.Session()

    # Create the S3 client
    s3_client = session.client('s3')

    # Upload text to S3
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=text.encode('utf-8')
    )

    return "Uploaded text to S3"

@app.route("/downloadFromS3/")
def downloadFromS3():
    bucket_name = 'textfiledata'
    person = str(request.args.get("person"))
    key = 'testingfolder/' + person + '.txt'

    # Create an S3 client using the system variables
    session = boto3.Session()

    # Create the S3 client
    s3_client = session.client('s3')

    # Download text from S3
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=key
    )

    text = response['Body'].read().decode('utf-8')

    return "Downloaded text from S3: " + text
