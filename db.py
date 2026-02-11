from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ai_recruitment"]
resume_logs = db["resume_ai_logs"]
