# nATS - New Applicant Tracking System

nATS is a web application built using Flask and Python, with AWS S3 for storing data and Pinecone for the vector database. It is an innovative Applicant Tracking System that utilizes semantic similarity based on embeddings to rank applicants for job positions.

## Features

- **Semantic Matching**: nATS employs embeddings to evaluate the semantic similarity between applicant resumes and job descriptions, enabling more accurate applicant ranking.
- **Job Management**: Add, view, and manage job listings within the system.
- **Applicant Management**: Create, track, and organize applicant profiles with their relevant details.
- **Data Storage**: Utilize AWS S3 to securely store applicant resumes and other data.
- **Integration with Pinecone**: Leverage Pinecone's vector database to store and query applicant and job embeddings efficiently.

## Prerequisites

Before running the application, make sure you have the following:

- Python 3.7 or higher installed on your machine.
- AWS S3 credentials and a configured bucket for storing data.
- Pinecone API key for setting up the vector database.

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
```

2. Navigate to the project directory:
```
cd nATS
```
3. Install the required dependencies:

```
pip install -r requirements.txt
```
4. Configure the environment variables:
```
        OPENAI_API_KEY: Your OpenAI API key.
        PINECONE_API_KEY: Your Pinecone API key.
        PINECONE_ENVR: The environment for Pinecone (e.g.,    "production" or "development").
        NATS_KEY: Secret key for Flask session management.
        FLASK_APP: "./api/index.py"
```

## Usage

1. Run the Flask development server:
```
flask run
```
2. Access the web application in your browser at http://localhost:5000.

3. Use the various features provided by the nATS web application to manage jobs, applicants, and match resumes to job descriptions effectively.

## Project Name: nATS - nATS Applicant Tracking System

The name of our project, nATS, holds an interesting history that reflects its evolution and purpose. Originally, it stood for "new Applicant Tracking System," signifying our aim to create a modern and innovative solution for managing applicants in the recruitment process.

As the project progressed, we embraced the uniqueness of our approach and decided to emphasize the departure from traditional applicant tracking systems. Thus, nATS also became an acronym for "not a Traditional tracking system," highlighting the novel features and capabilities we introduced.

Finally, nATS evolved into a self-referencing recursive acronym, representing "nATS Applicant tracking system."

This name transformation encapsulates the project's evolution.
.
