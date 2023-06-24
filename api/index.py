from flask import Flask
from flask import render_template
from flask import send_file, request
import os 
import openai
import boto3 
import pinecone
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests


openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv('PINECONE_ENVR')) 

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

@app.route("/applicants")
def applicants():
    return render_template('applicants.html')

@app.route("/getEmbedding/<text>")
def getEmbeding(text):
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
        return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]
    embedding = get_embedding(text, model="text-embedding-ada-002")
    #printing only for debugging purposes
    print(embedding)
    return embedding

@app.route("/addVector/")
#this is just because we currently have only one pod on the free version of pinecone
def addVector():
    index = pinecone.Index('hacksstart') 
    vector = []
    dataType = ''
    if request.method=='GET':
        vector = request.args.get("vector")
        dataType = request.args.get("dataType")
    elif request.method=='POST':
        vector = request.form["vector"]
        dataType = request.form.get("dataType")
    upsert_response = index.upsert(
        vectors=[
            {
            'id':'addtest3', 
            'values': vector, 
            'metadata':{'datatType': dataType}}
            ]
            ,
        namespace='example-namespace'
    )
    print(upsert_response)
    return "Vector successfully added!"



@app.route("/saveData/")
def saveData():
    index = pinecone.Index('hacksstart') 
    dataType = ''
    text =''
    id = ''
    if request.method=='GET':
        dataType = request.args.get("dataType")
        text = request.args.get("text")
        id = request.args.get("id")
    elif request.method=='POST':
        dataType = request.form["dataType"]
        text = request.form["text"]
        id = request.args.get("id")
    vector = getEmbeding(text)    
    upsert_response = index.upsert(
        vectors=[
            {
            'id': id, 
            'values':vector, 
            'metadata':{'dataType': dataType, 'content': text}}
        ],
        namespace='example-namespace'
    )
    return "Data successfully saved!"
    

@app.route("/saveToS3/")
def saveToS3():
    dataType = ''
    text =''
    id = ''
    if request.method=='GET':
        dataType = request.args.get("dataType")
        text = request.args.get("text")
        id = request.args.get("id")
    elif request.method=='POST':
        dataType = request.form["dataType"]
        text = request.form["text"]
        id = request.args.get("id")
    
    bucket_name = 'textfiledata'
    key = dataType + '/' + id + '.txt'

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
    print(response)
    return "Save to S3 is successful"
