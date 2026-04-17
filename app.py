from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from uuid6 import uuid7
from datetime import datetime, timezone
import requests
from requests.exceptions import RequestException

# Load .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.profile_db
collection = db.users


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE'
    return response


def get_age_group(age):
    if age <= 12:
        return 'child'
    elif age <= 19:
        return 'teenager'
    elif age <= 59:
        return 'adult'
    else:
        return 'senior'

def serialize_profile(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "gender": p["gender"],
        "gender_probability": p["gender_probability"],
        "sample_size": p["sample_size"],
        "age": p["age"],
        "age_group": p["age_group"],
        "country_id": p["country_id"],
        "country_probability": p["country_probability"],
        "created_at": p["created_at"]
    }

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing or empty name",
        }), 400

    if not isinstance(data["name"], str):
        return jsonify({
            "status": "error",
            "message": "Invalid type for name",
        }), 422

    name = data['name'].strip().lower()


    # Idempotency
    existing = collection.find_one({"name": name})
    if existing:
        existing.pop("_id", None)
        return jsonify({
            "status": "success",
            "message": "Profile already exists",
            "data": serialize_profile(existing)
        }), 200
    try:
        # External APIs
        g = requests.get(f'https://api.genderize.io?name={name}').json()
        a = requests.get(f'https://api.agify.io?name={name}').json()
        n = requests.get(f'https://api.nationalize.io?name={name}').json()

        if not g.get('gender') or g.get('count') == 0:
            return jsonify({
                "status": "error",
                "message": "Genderize returned an invalid response"
            }), 502

        if a.get('age') is None:
            return jsonify({
                "status": "error",
                "message": "Agify returned an invalid response"
            }), 502

        if not n.get('country'):
            return jsonify({
                "status": "error",
                "message": "Nationalize returned an invalid response"
            })

        age = a["age"]
        age_group = get_age_group(age)
        best_country = max(n["country"], key=lambda x: x["probability"])

        profile = {
            "id": str(uuid7()),
            "name": name,
            "gender": g["gender"],
            "gender_probability": g["probability"],
            "sample_size": g["count"],
            "age": age,
            "age_group": age_group,
            "country_id": best_country["country_id"],
            "country_probability": best_country["probability"],
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        collection.insert_one(profile)

        return jsonify({
            "status": "success",
            "data": serialize_profile(profile)
        }), 201

    except RequestException:
        return jsonify({
            "status": "error",
            "message": "Upstream or server failure"
        }), 502


@app.route('/api/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = collection.find_one({"id": profile_id})
    if not profile:
        return jsonify({
            "status": "error",
            "message": "Profile not found",
        }), 404

    return jsonify({
        "status": "success",
        "data": serialize_profile(profile)
    }), 200


@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    query = {}
    gender = request.args.get("gender")
    country_id = request.args.get("country_id")
    age_group = request.args.get("age_group")

    if gender:
        query["gender"] = gender.lower()

    if country_id:
        query["country"] = country_id.upper()

    if age_group:
        query["age_group"] = age_group.lower()

    profiles = list(collection.find(query))

    return jsonify({
            "status": "success",
            "count": len(profiles),
            "data": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "gender": p["gender"],
                    "age": p["age"],
                    "age_group": p["age_group"],
                    "country": p["country"]
                }
                for p in profiles
            ]
        }), 200

@app.route('/api/profiles/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    result = collection.delete_one({"id": profile_id})
    if result.deleted_count == 0:
        return jsonify({
            "status": "error",
            "message": "Profile not found",
        }), 404

    return '', 204


if __name__ == "__main__":
    app.run(debug=True)
