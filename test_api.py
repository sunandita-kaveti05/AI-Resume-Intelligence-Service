# test_api.py
import requests

url = "http://127.0.0.1:8000/analyze"

# The data part (Job Description)
data = {
    "jd_text": "Looking for a Machine Learning Engineer with Python, Docker, and SQL experience."
}

# The file part (Resume)
files = {
    "file": ("c:\Users\sun05\OneDrive\Desktop\Resume\Sun_resume.pdf", open("path/to/your/resume.pdf", "rb"), "application/pdf")
}

response = requests.post(url, data=data, files=files)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())