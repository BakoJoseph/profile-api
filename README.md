## 🌐 Live API

https://your-app.up.railway.app

# Profile API 🚀

A RESTful API that generates user profiles from a name by integrating
multiple external APIs, applying classification logic, storing results
in MongoDB, and exposing endpoints to manage the data.

## Setup & Run Locally

1.  Clone repo git clone
    https://github.com/your-username/profile-api.git cd profile-api

2.  Create virtual env python -m venv .venv

Activate: Windows: .venv`\Scripts`{=tex}`\activate`{=tex} Mac/Linux:
source .venv/bin/activate

3.  Install dependencies pip install -r requirements.txt

4.  Create .env MONGO_URI=your_mongodb_connection_string PORT=5000

5.  Run app python app.py

## Endpoints

### Create Profile

POST /api/profiles

Body:
{
  "name": "john"
}

GET /api/profiles
GET /api/profiles/{id} 
DELETE /api/profiles/{id}

### Filtering Examples

GET /api/profiles?gender=male  
GET /api/profiles?age_group=adult  
GET /api/profiles?country_id=NG  

## Edge Cases

- Duplicate names return existing profile
- No matching filter returns empty array
- External API failure returns 502

## Deployment

Deployed on Railway using Gunicorn:

gunicorn -w 4 -b 0.0.0.0:$PORT app:app

## CORS

Access-Control-Allow-Origin: *

## Notes

-   Case-insensitive filtering
-   Returns empty array if no data
-   Uses MongoDB
