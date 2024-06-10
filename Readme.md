# API Usage Dashboard Application

This project is a web-based dashboard for monitoring API usage. It utilizes Flask for the web server and Dash for interactive components.

## Prerequisites

Before you run the application, you will need:
- Python 3.6 or later
- pip (Python package installer)
- Access to MongoDB and a valid MongoDB URI

## Installation

Follow these steps to set up the application locally:

### Clone the Repository

If you have this code in a repository, you can clone it using Git. Otherwise, ensure you have `app.py` and `requirements.txt` in your working directory.

```bash
git clone <your-repository-url>
cd <repository-name>
```

### Install Dependencies
Install the required Python libraries using pip:

```bash
pip install -r requirements.txt
```
### Environment Setup
Create a .env file in the same directory as app.py to store environment variables:

```bash
python app.py
```
This command starts the Flask server with the dashboard accessible locally. By default, the application will be available at http://localhost:5000, and it will redirect you to the dashboard at /dashboard/.

