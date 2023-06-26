from flask import Flask
from flask import render_template
from flask import send_file, request, session, jsonify
import os 
import openai
import boto3 
import pinecone
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests


openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv('PINECONE_ENVR')) 

app = Flask(__name__)
app.secret_key = os.getenv("NATS_KEY")
app.config['SESSION_TYPE'] = 'filesystem'

@app.before_first_request
def startSession():
    session["jobIds"] = []
    session["applicantIds"] = []

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
    try:
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
    except Exception as e:
        app.logger.error(f"Error uploading to S3: {str(e)}")
        error_message = "Error uploading to S3. Please try again later."
        return jsonify(error=error_message), 500

@app.route("/downloadFromS3/")
def downloadFromS3():
    try:
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
    except Exception as e:
        app.logger.error(f"Error downloading from S3: {str(e)}")
        error_message = "Error downloading from S3. Please try again later."
        return jsonify(error=error_message), 500

@app.route("/applicants")
def applicants():
    return render_template('applicants.html')

@app.route("/getEmbedding/<text>")
def getEmbedding(text):
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
    try:
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
    except Exception as e:
        app.logger.error(f"Error adding vector to Pinecone: {str(e)}")
        error_message = "Error adding vector to Pinecone. Please try again later."
        return jsonify(error=error_message), 500




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
    vector = getEmbedding(text)    
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
 
def uploadData(dataType, text, id):
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
        
    uploadData(dataType, text, id)
    #print(response)
    return "Save to S3 is successful"

@app.route("/createJob/", methods=['GET', 'POST'])
def createJob():
    print("Creating Job...")
    jobTitle = ''
    jobDescription = ''
    jobLocation = ''
    jobId = ''
    if request.method=='GET':
        jobTitle = request.args.get("jobTitle")
        jobDescription = request.args.get("jobDescription")
        jobId = request.args.get("jobId")
        jobLocation = request.args.get("jobLocation")
    elif request.method=='POST':
        jobTitle = request.json["jobTitle"]
        jobDescription = request.json["jobDescription"]
        jobId = request.json["jobId"]
        jobLocation = request.json["jobLocation"]
    session["jobIds"].append(jobId)
    titleKey = jobId + '-' + 'title'
    descriptionKey = jobId + '-' + 'description'
    locationKey = jobId + '-' + 'location'
    session[titleKey] = jobTitle
    session[descriptionKey] = jobDescription
    session[locationKey] = jobLocation
    uploadData('Jobs', jobTitle, jobId)
    print("Finished Creating Job!")
    return "SUCCESS"

@app.route("/getJobs/", methods=['POST', 'GET'])
def getJobs():
    print("Getting jobs..")
    jobIds = session["jobIds"]
    jobs = []
    for id in jobIds:
        titleKey = id + '-' + 'title'
        descriptionKey = id + '-' + 'description'
        locationKey = id + '-' + 'location'
        title = session[titleKey]
        description = session[descriptionKey]
        location = session[locationKey]
        job = {
            "jobId": id,
            "jobTitle": title,
            "jobLocation": location,
            "jobDescription": description
        }
        jobs.append(job)
    print(jobs)
    return jsonify(jobs)
        
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {str(e)}")
    error_message = "An error occurred. Please try again later."
    return jsonify(error=error_message), 500

def matchText(text):
    index = pinecone.Index('hacksstart') 
    inputVector = getEmbedding(text)
    query_response = index.query(
    namespace='example-namespace',
    top_k=1,
    include_values=True,
    include_metadata=True,
    vector= inputVector,
    filter={
        'dataType': 'job'
    }
    )
    qstring = query_response.to_str()
    return jsonify(qstring)

@app.route("/match/", methods=['GET','POST'])
def match():
    text = ""
    if request.method=='GET':
        text = request.args.get("text")
    elif request.method=='POST':
        inputVector = request.form["vector"]
        text = request.form("text")
    response = matchText(text)
    return response

@app.route("/createApplicant/", methods=['GET', 'POST'])
def createApplicant():
    print("Creating Applicant...")
    name = ''
    job = ''
    applicantID = ''
    skills = ''
    education = ''
    experience = ''
    if request.method=='GET':
        name = request.args.get("name")
        job = request.args.get("job")
        applicantID = request.args.get("applicantID")
        skills = request.args.get("skills")
        education = request.args.get("education")
        experience = request.args.get("experience")
    elif request.method=='POST':
        name = request.json["name"]
        job = request.json["job"]
        applicantID = request.json["applicantID"]
        skills = request.json["skills"]
        education = request.json["education"]
        experience = request.json["experience"]
    session["applicantIds"].append(applicantID)
    nameKey = applicantID + '-' + 'name'
    jobKey = applicantID + '-' + 'job'
    skillsKey = applicantID + '-' + 'skills'
    educationKey = applicantID + '-' + 'education'
    experienceKey = applicantID + "-" + 'experience'
    session[nameKey] = name
    session[jobKey] = job
    session[skillsKey] = skills
    session[educationKey] = education
    session[experienceKey] = experience
    resume = name + '\n\n' + job + '\n\n' + skills + '\n\n' + education + '\n\n' + experience
    uploadData('Applicant', resume, applicantID)
    print("Finished Creating Applicant!")
    return "SUCCESS"

@app.route("/getApplicants/", methods=['POST', 'GET'])
def getApplicants():
    print("Getting applicants..")
    applicantIds = session["applicantIds"]
    applicants = []
    for id in applicantIds:
        nameKey = id + '-' + 'name'
        jobKey = id + '-' + 'job'
        skillsKey = id + '-' + 'skills'
        educationKey = id + '-' + 'education'
        experienceKey = id + "-" + 'experience'
        name = session[nameKey]
        job = session[jobKey]
        skills = session[skillsKey]
        education = session[educationKey]
        experience = session[experienceKey]
        applicant = {
            "applicantId": id,
            "name": name,
            "job": job,
            "skills": skills,
            "education": education,
            "experience": experience
        }
        applicants.append(applicant)
    print(applicants)
    return jsonify(applicants)

@app.route("/matches")
def toMatch():
    return render_template("matches.html")

@app.route("/matched/")
def toMatchWithJobId():
    print("Matching...")
    id = ''
    if request.method=='GET':
        id = request.args.get("id")
    # titleKey = id + '-' + 'title'
    # descriptionKey = id + '-' + 'description'
    # locationKey = id + '-' + 'location'
    # job = {
    #     "jobId": id,
    #     "title": session[titleKey],
    #     "location": session[locationKey],
    #     "description": session[descriptionKey]
    # }
    # embeddable = session[titleKey] + '\n\n' + session[descriptionKey]
    # print(embeddable)   
    #results = matchText(embeddable)
    #print(results)
    # matchContents = {
    #     "job": job,
    #     "results": results
    # }
    print("Finished Matching!")
    return render_template("./aftermatch.html")