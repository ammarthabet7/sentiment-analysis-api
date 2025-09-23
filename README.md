# Sentiment Analysis API (MLOps Project)

A production-grade RESTful API for sentiment analysis, deployed on AWS with a fully automated CI/CD pipeline.

---

### ► Core Features
- **Live API:** Serves real-time sentiment analysis requests.
- **Automated Pipeline:** Fully automated testing and deployment using GitHub Actions.
- **Cloud Hosted:** Runs on a stable AWS EC2 and RDS infrastructure.
- **Production Architecture:** Uses Nginx as a reverse proxy for security and performance.
- **Data Persistence:** Stores all analysis results in a PostgreSQL database.

---

### ► Tech Stack
- **Backend:** Python, FastAPI
- **ML Model:** TextBlob
- **Database:** PostgreSQL (on AWS RDS)
- **Infrastructure:** AWS EC2, Elastic IP, Nginx
- **CI/CD:** GitHub Actions, pytest, Shell Scripting
- **Version Control:** Git, GitHub

---

### ► How It Works: The CI/CD Pipeline
When code is pushed to the `main` branch:

1.  **Test Job:**
    -   Installs all dependencies.
    -   Runs the `pytest` test suite to ensure code quality.

2.  **Deploy Job:**
    -   Connects securely to the AWS EC2 server.
    -   Pulls the latest code from GitHub.
    -   Performs a safe, graceful restart of the API.
    -   Verifies the new version is live and healthy via a health check.

---

### ► Local Development Setup

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```
*(On Windows, use: `venv\Scripts\activate`)*

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the local server:**
```bash
uvicorn main:app --reload
```
- API Docs will be available at: `http://127.0.0.1:8000/docs`
