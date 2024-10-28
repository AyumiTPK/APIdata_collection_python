import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = os.getenv("API_ID")
APP_KEY = os.getenv("API_KEY")

# Set job search parameters
keywords = ["Power BI", "Tableau", "Visualization"]
base_url = f"https://api.adzuna.com/v1/api/jobs/ch/search/1"

# Connect to SQLite database and create table if it doesn't exist
conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        title TEXT,
        company TEXT,
        location TEXT,
        category TEXT,
        description TEXT,
        url TEXT,
        keywords TEXT
    )
''')
conn.commit()

# Create a function to fetch jobs based on keywords
def fetch_jobs(keyword):
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'what': keyword,
        'results_per_page': 20,
        'content-type': 'application/json'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Failed to fetch data for keyword '{keyword}' with status code: {response.status_code}")
        return []

# Insert job data
def insert_job(job_info):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, location, category, description, url, keywords)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (job_info['Title'], job_info['Company'], job_info['Location'], job_info['Category'], job_info['Description'], job_info['URL'], job_info['Keywords']))
    conn.commit()

# Collect all jobs based on keywords
all_jobs = []
for keyword in keywords:
    print(f"Fetching jobs for keyword: {keyword}")
    jobs = fetch_jobs(keyword)
    for job in jobs:
        job_info = {
            'Title': job.get('title'),
            'Company': job.get('company', {}).get('display_name'),
            'Location': job.get('location', {}).get('display_name'),
            'Category': job.get('category', {}).get('label'),
            'Description': job.get('description'),
            'URL': job.get('redirect_url'),
            'Keywords': keyword
        }
        all_jobs.append(job_info)

# Example of inserting a job
for job in all_jobs:
    insert_job(job)

conn.close()