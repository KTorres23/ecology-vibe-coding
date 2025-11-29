from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

JOBS_URL = "https://jobs.rwfm.tamu.edu/search/"

@app.route('/api/jobs')
def get_jobs():
    resp = requests.get(JOBS_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    jobs = []
    # Update selectors below based on actual job card HTML structure
    for card in soup.select('.job-card, .job-listing, .job'):
        title = card.select_one('.job-title')
        link = card.select_one('a')
        location = card.select_one('.job-location')
        desc = card.select_one('.job-description')
        jobs.append({
            'title': title.text if title else 'No title',
            'link': link['href'] if link else '#',
            'location': location.text if location else '',
            'description': desc.text if desc else ''
        })
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True)
