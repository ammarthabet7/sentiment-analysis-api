Production-Grade Sentiment Analysis API
This project implements a complete, production-ready system for serving a sentiment analysis model via a RESTful API. The primary focus is on building a robust, automated MLOps pipeline for continuous integration and deployment on cloud infrastructure.

Project Overview
The system is designed to provide real-time sentiment analysis (positive, negative, neutral) for a given text input. All analysis results are persisted in a relational database for future analytics. The entire workflow, from code commit to live deployment, is fully automated.

The architecture follows industry best practices, separating concerns between the application layer, the web server, and the database.

Core Features
RESTful API: A high-performance asynchronous API built with FastAPI.
Data Persistence: All sentiment analysis requests and results are stored in a PostgreSQL database.
Automated CI/CD: A complete GitHub Actions pipeline automates all testing and deployment procedures.
Zero-Downtime Deployments: The deployment script is engineered for high availability, using health checks and PID management to ensure seamless updates without service interruption.
Cloud Infrastructure: The entire stack is deployed and configured on Amazon Web Services (AWS).
Reverse Proxy: Nginx is configured as a reverse proxy to manage incoming traffic and provide a secure, scalable entry point to the application.
Technical Architecture
The system is composed of several key components:

Application: A Python application built with the FastAPI framework. It exposes endpoints for analysis, health checks, and metrics.
Database: A PostgreSQL database, managed by AWS RDS, for storing all transactional data.
Web Server: An AWS EC2 instance running Ubuntu Linux serves as the host for the application and reverse proxy.
Reverse Proxy: Nginx is deployed to handle public HTTP traffic on port 80 and proxy requests to the FastAPI application running on an internal port.
CI/CD: GitHub Actions orchestrates the entire pipeline, triggered on every push to the main branch.
CI/CD Pipeline Breakdown
The deployment workflow is defined in .github/workflows/deploy.yml and consists of two main jobs:

test Job:

Checks out the source code.
Sets up a Python environment and installs dependencies.
Runs the automated test suite using pytest to validate the application's integrity.
deploy Job:

This job only runs if the test job succeeds and the push is to the main branch.
Securely connects to the AWS EC2 instance via SSH.
Pulls the latest version of the source code from the repository.
Installs or updates Python dependencies within the dedicated virtual environment.
Performs a graceful restart of the application using a PID file for precise process management.
Enters a health-check loop, polling the /health endpoint to verify the new version is running correctly before completing the deployment.
Local Development Setup
To run this project locally, you will need Python 3.9+ and Git installed.

Clone the repository:

bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Create a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:

bash
pip install -r requirements.txt
Run the application:
The application is configured to use a local SQLite database for development by default.

bash
uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000. The interactive documentation can be accessed at http://127.0.0.1:8000/docs.
