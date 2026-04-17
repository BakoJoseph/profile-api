# 🚀 Profile API

A RESTful API that generates user profiles from a name using multiple external APIs, applies classification logic, stores results in MongoDB, and exposes endpoints to manage and query the data.

---

## 🌐 Live API

https://profile-api-production-da51.up.railway.app

---

## 🛠 Tech Stack

- Python (Flask)
- MongoDB (PyMongo)
- Requests
- Gunicorn

---

## ⚙️ Run Locally

### 1. Clone the repo
git clone https://github.com/BakoJoseph/profile-api.git
cd profile-api

### 2. Create virtual environment
python -m venv .venv

Activate:
Windows:
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate

---

### 3. Install dependencies
pip install -r requirements.txt

---

### 4. Create .env
MONGO_URI=your_mongodb_connection_string
PORT=5000

---

### 5. Run app
python app.py

---

## 📡 API Endpoints

### ✅ Create Profile
POST /api/profiles

Body:
{
  "name": "john"
}

---

### 🔁 Idempotency
If name exists:
{
  "status": "success",
  "message": "Profile already exists",
  "data": { ... }
}

---

### ✅ Get All Profiles
GET /api/profiles

---

### 🔍 Filtering (Case-Insensitive)
GET /api/profiles?gender=male  
GET /api/profiles?age_group=adult  
GET /api/profiles?country_id=NG  

---

### ✅ Get Single Profile
GET /api/profiles/{id}

---

### ✅ Delete Profile
DELETE /api/profiles/{id}

Returns:
204 No Content

---

## 🧠 Classification Logic

Age Groups:
0–12 → child  
13–19 → teenager  
20–59 → adult  
60+ → senior  

---

## ⚠️ Error Handling

{
  "status": "error",
  "message": "Error message"
}

Codes:
400 → Missing name  
404 → Not found  
502 → External API failure  

---

## 🚨 Edge Cases

- Duplicate names return existing profile  
- No matching filter returns empty array  
- External API failure returns 502  

---

## 🔐 CORS

Access-Control-Allow-Origin: *

---

## 🚀 Deployment

gunicorn -w 4 -b 0.0.0.0:$PORT app:app

---

## 📦 Requirements

Flask  
pymongo  
requests  
gunicorn  
python-dotenv  

---

## 👨‍💻 Author

Bako Olamide