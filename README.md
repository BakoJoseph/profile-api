# 🚀 Insighta Labs - Backend Intelligence API

## Live API 
https://insighta-profile-api-production.up.railway.app

## 📌 Overview
This project is a backend API built for Insighta Labs to manage demographic profile data.
It supports filtering, sorting, pagination, and natural language queries.

---

## 🛠 Tech Stack
- Python (Flask)
- MongoDB Atlas
- PyMongo

---

## ⚙️ Setup Instructions

1. Clone the repo's branch
```bash
git clone https://github.com/BakoJoseph/profile-api.git/tree/profile-api-II
cd your-repo
```

2. Create virtual environment
```bash
python -m venv venv
```

Activate:

Windows:
```bash 
venv\Scripts\activate
```

Mac/Linux:

```bash 
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create .env file
MONGO_URI=your_mongodb_connection_string

5. Run the server
```bash
python app.py
```

Server runs on:
http://127.0.0.1:5000

---

## 🌱 Data Seeding

Run:
python seed.py

- Seeds 2026 profiles
- Prevents duplicates

---

## 📡 API Endpoints

### Create Profile

```bash
POST /api/profiles
```

Request:
```JSON
{
  "name": "emmanuel"
}
```
Response:
```JSON
{
  "_id": "69eadba112e61cf7028bfa9b",
  "name": "emmanuel",
  "age": 68,
  "age_group": "senior",
  "country_id": "NG",
  "country_name": "Nigeria",
  "country_probability": 0.6,
  "created_at": "2026-04-24T02:55:32.802603Z",
  "gender": "male",
  "gender_probability": 0.66,
  "id": "019dbd69-fbc2-767b-8fc9-bbd46effddaf"
}
```

---

### Get All Profiles

```bash
GET /api/profiles
```
QueryParameters:
```bash
gender
age_group
country_id
min_age / max_age
min_gender_probability
min_country_probability
sort_by = age | created_at | gender_probability
order = asc | desc
page=1
limit=10
```

Example:
```bash
/api/profiles?gender=male&country_id=NG&min_age=25&sort_by=age&order=desc&page=1&limit=10
```

---

### Get Single Profile

```bash
GET /api/profiles/<id>
```

---

### Delete Profile

```bash
DELETE /api/profiles/<id>
```

---

### Natural Language Search

```bash
GET /api/profiles/search?q=
```

Example:
```bash
/api/profiles/search?q=young males from nigeria
```

---

## 🧠 Natural Language Parsing

This project uses rule-based parsing (no AI)

Supported queries:

Query
---
young males             gender=male + age 16–24  
---
females above 30        gender=female + age ≥ 30  
---
people from angola      country_id=AO  
---
adult males from kenya  gender=male + age_group=adult + country_id=KE  
---
male and female 
teenagers above 17      age_group=teenager + age ≥ 17  

---

##  Parsing Logic

- Uses regex for keyword detection
- Supports plural words (male/males felame/females)
- Detects both genders and igonres gender filter 
- Merges age filters into a single objects
- Maps country names to ISO codes

Example Logic:

```Python
if "young" in q :
  age_filter["$gte"] = 16
  age_filter["$lte"] = 24

if re.search(r"\bmale(s)?\b", q)
  query["gender"] = "male"
```

## ⚠️ Limitations

- Only predefined countries names supported
- No fuzzy matching(exact keyword only)
- Only simple keyword parsing
- Cannot handle complex sentences

---

## ❌ Error Format

```bash
{
  "status": "error",
  "message": "error message"
}
```

---

## 🌍 CORS
```http
Access-Control-Allow-Origin: *
```

---

## 🏁 Notes

- UUID v7 used for IDS
- Timestamps are UTC ISO 8601 
- Pagination Max limit = 50
- No full-table scans (queries are filtered)
