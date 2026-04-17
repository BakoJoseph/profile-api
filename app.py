from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import uuid
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["profile_db"]
collection = db["profiles"]


# ---------------------------
# Helper Functions
# ---------------------------

def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"


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


# ---------------------------
# Routes
# ---------------------------

# CREATE PROFILE
@app.route("/api/profiles", methods=["POST"])
def create_profile():
    data = request.get_json()

    if not data or "name" not in data or not data["name"]:
        return jsonify({
            "status": "error",
            "message": "Missing or empty name"
        }), 400

    name = data["name"].lower()

    # Check if exists (idempotency)
    existing = collection.find_one({"name": name})
    if existing:
        return jsonify({
            "status": "success",
            "message": "Profile already exists",
            "data": serialize_profile(existing)
        }), 200

    try:
        # Call external APIs
        g = requests.get(f"https://api.genderize.io?name={name}").json()
        a = requests.get(f"https://api.agify.io?name={name}").json()
        n = requests.get(f"https://api.nationalize.io?name={name}").json()

        # Edge cases
        if g.get("gender") is None or g.get("count", 0) == 0:
            return jsonify({
                "status": "error",
                "message": "Genderize returned an invalid response"
            }), 502

        if a.get("age") is None:
            return jsonify({
                "status": "error",
                "message": "Agify returned an invalid response"
            }), 502

        if not n.get("country"):
            return jsonify({
                "status": "error",
                "message": "Nationalize returned an invalid response"
            }), 502

        age = a["age"]
        age_group = get_age_group(age)

        best_country = max(n["country"], key=lambda x: x["probability"])

        profile = {
            "id": str(uuid.uuid4()),
            "name": name,
            "gender": g["gender"].lower(),
            "gender_probability": g["probability"],
            "sample_size": g["count"],
            "age": age,
            "age_group": age_group,
            "country_id": best_country["country_id"],
            "country_probability": best_country["probability"],
            "created_at": datetime.utcnow().isoformat()
        }

        collection.insert_one(profile)

        return jsonify({
            "status": "success",
            "data": serialize_profile(profile)
        }), 201

    except requests.exceptions.RequestException:
        return jsonify({
            "status": "error",
            "message": "Upstream or server failure"
        }), 502


# GET ALL PROFILES (WITH FILTERING)
@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    query = {}

    gender = request.args.get("gender")
    country_id = request.args.get("country_id")
    age_group = request.args.get("age_group")

    if gender:
        query["gender"] = gender.lower()

    if country_id:
        query["country_id"] = country_id.upper()

    if age_group:
        query["age_group"] = age_group.lower()

    profiles = list(collection.find(query))

    result = []
    for p in profiles:
        result.append({
            "id": p["id"],
            "name": p["name"],
            "gender": p["gender"],
            "age": p["age"],
            "age_group": p["age_group"],
            "country_id": p["country_id"]
        })

    return jsonify({
        "status": "success",
        "count": len(result),
        "data": result
    }), 200


# GET SINGLE PROFILE
@app.route("/api/profiles/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    profile = collection.find_one({"id": profile_id})

    if not profile:
        return jsonify({
            "status": "error",
            "message": "Profile not found"
        }), 404

    return jsonify({
        "status": "success",
        "data": serialize_profile(profile)
    }), 200


# DELETE PROFILE
@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    result = collection.delete_one({"id": profile_id})

    if result.deleted_count == 0:
        return jsonify({
            "status": "error",
            "message": "Profile not found"
        }), 404

    return "", 204


# ---------------------------
# CORS (VERY IMPORTANT)
# ---------------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)