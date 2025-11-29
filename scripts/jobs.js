// jobs.js
// Scrapes job postings from Texas A&M Natural Resources Job Board and displays them on jobs.html

const JOBS_API_URL = 'http://localhost:5000/api/jobs';

async function fetchJobs() {
    const loading = document.getElementById('loading');
    const jobsList = document.getElementById('jobs-list');
    loading.style.display = 'block';
    jobsList.innerHTML = '';

    try {
        const response = await fetch(JOBS_API_URL);
        if (!response.ok) throw new Error('Network response was not ok');
        const jobs = await response.json();
        if (jobs.length === 0) {
            jobsList.innerHTML = '<p>No jobs found.</p>';
        } else {
            jobs.forEach(job => {
                jobsList.innerHTML += `
                    <div class="job-posting">
                        <h3><a href="${job.link}" target="_blank">${job.title}</a></h3>
                        <p>${job.location}</p>
                        <p>${job.description}</p>
                    </div>
                `;
            });
        }
    } catch (error) {
        jobsList.innerHTML = `<p>Could not load jobs. Is your backend running?</p>`;
    } finally {
        loading.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', fetchJobs);