# 🚀 Profile API 

## 📌 Overview

This API accepts a name, calls external APIs (**Genderize, Agify,
Nationalize**), processes the data, stores it in MongoDB, and exposes
endpoints to manage profiles.

------------------------------------------------------------------------

## 🌐 Base URL

https://your-app.up.railway.app

------------------------------------------------------------------------

## 📡 Endpoints

### 1️⃣ Create Profile

POST /api/profiles

Request: { "name": "ella" }

Response (201): { "status": "success", "data": { "id": "uuid", "name":
"ella", "gender": "female", "gender_probability": 0.99, "sample_size":
1234, "age": 46, "age_group": "adult", "country_id": "US",
"country_probability": 0.85, "created_at": "2026-04-01T12:00:00Z" } }

------------------------------------------------------------------------

### 2️⃣ Get Single Profile

GET /api/profiles/{id}

------------------------------------------------------------------------

### 3️⃣ Get All Profiles

GET /api/profiles

Query params: - gender - country_id - age_group

------------------------------------------------------------------------

### 4️⃣ Delete Profile

DELETE /api/profiles/{id}

------------------------------------------------------------------------

## ⚙️ Tech Stack

-   Python (Flask)
-   MongoDB
-   PyMongo
-   Requests

------------------------------------------------------------------------

## 🛠️ Setup

python -m venv .venv source .venv/Scripts/activate pip install -r
requirements.txt

Create .env: MONGO_URI=your_mongodb_uri

Run: python app.py

------------------------------------------------------------------------

## 🚀 Deployment

Railway

------------------------------------------------------------------------

## 👤 Author

Bako Olamide Joseph
