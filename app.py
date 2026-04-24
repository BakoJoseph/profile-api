from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import uuid6
from datetime import datetime, timezone
import os
from parser import parse_query

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["profile_db"]
collection = db["profiles"]

# ---------------------------
# Helpers
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

country_name = {
    "NG": "Nigeria",
    "KE": "Kenya",
    "AO": "Angola",
    "GH": "Ghana",
    "TZ": "Tanzania",
    "UG": "Uganda",
    "ZA": "South Africa"
}

def serialize_profile(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "gender": p["gender"],
        "gender_probability": p["gender_probability"],
        "age": p["age"],
        "age_group": p["age_group"],
        "country_id": p["country_id"],
        "country_name": p["country_name"],
        "country_probability": p["country_probability"],
        "created_at": p["created_at"]
    }

# ---------------------------
# CREATE PROFILE
# ---------------------------

@app.route("/api/profiles", methods=["POST"])
def create_profile():
    data = request.get_json()

    if not data or "name" not in data or not data["name"]:
        return jsonify({"status": "error", "message": "Missing or empty name"}), 400

    name = data["name"].lower()

    existing = collection.find_one({"name": name})
    
    if existing:
        return jsonify({
            "status": "success",
            "message": "Profile already exists",
            "data": serialize_profile(existing)
        }), 200

    try:
        g = requests.get(f"https://api.genderize.io?name={name}").json()
        a = requests.get(f"https://api.agify.io?name={name}").json()
        n = requests.get(f"https://api.nationalize.io?name={name}").json()

        if g.get("gender") is None or g.get("count", 0) == 0:
            return jsonify({"status": "error", "message": "Genderize returned an invalid response"}), 502

        if a.get("age") is None:
            return jsonify({"status": "error", "message": "Agify returned an invalid response"}), 502

        if not n.get("country"):
            return jsonify({"status": "error", "message": "Nationalize returned an invalid response"}), 502

        best_country = max(n["country"], key=lambda x: x["probability"])

        code = best_country["country_id"]

        profile = {
            "id": str(uuid6.uuid7()),
            "name": name,
            "gender": g["gender"].lower(),
            "gender_probability": g["probability"],
            "age": a["age"],
            "age_group": get_age_group(a["age"]),
            "country_id": best_country["country_id"],
            "country_name": country_name.get(code, code),
            "country_probability": best_country["probability"],
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        collection.insert_one(profile)

        return jsonify({"status": "success", "data": serialize_profile(profile)}), 201

    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "Upstream or server failure"}), 502


# ---------------------------
# GET ALL PROFILES
# ---------------------------

@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    try:
        query = {}

        gender = request.args.get("gender")
        age_group = request.args.get("age_group")
        country_id = request.args.get("country_id")

        min_age = request.args.get("min_age", type=int)
        max_age = request.args.get("max_age", type=int)

        min_gender_prob = request.args.get("min_gender_probability", type=float)
        min_country_prob = request.args.get("min_country_probability", type=float)

        if gender:
            query["gender"] = gender.lower()

        if age_group:
            query["age_group"] = age_group.lower()

        if country_id:
            query["country_id"] = country_id.upper()

        if min_age is not None or max_age is not None:
            query["age"] = {}
            if min_age is not None:
                query["age"]["$gte"] = min_age
            if max_age is not None:
                query["age"]["$lte"] = max_age

        if min_gender_prob is not None:
            query["gender_probability"] = {"$gte": min_gender_prob}

        if min_country_prob is not None:
            query["country_probability"] = {"$gte": min_country_prob}

        sort_by = request.args.get("sort_by", "created_at")
        order = request.args.get("order", "asc")

        allowed_sort_fields = ["age", "created_at", "gender_probability"]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        sort_order = 1 if order == "asc" else -1

        # Pagination (STRICT)
        page_param = request.args.get("page")
        limit_param = request.args.get("limit")

        try:
            page = int(page_param) if page_param else 1
            limit = int(limit_param) if limit_param else 10
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid query parameters"
            }), 422

        if page < 1 or limit < 1 or limit > 50:
            return jsonify({
            "status": "error",
            "message": "Invalid query parameters"
        }), 422


        skip = (page - 1) * limit

        cursor = collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        total = collection.count_documents(query)

        data = [serialize_profile(p) for p in cursor]

        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 422


# ---------------------------
# SEARCH
# ---------------------------

@app.route("/api/profiles/search", methods=["GET"])
def search_profiles():
    q = request.args.get("q")

    if not q:
        return jsonify({"status": "error", "message": "Missing query"}), 400

    filters = parse_query(q)

    print("Passed filters:" , filters)

    if filters is None:
        return jsonify({"status": "error", "message": "Unable to interpret query"}), 400

    page_param = request.args.get("page")
    limit_param = request.args.get("limit")
    try:
        page = int(page_param) if page_param else 1
        limit = int(limit_param) if limit_param else 10
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid query parameters"
        }), 422
    
    if page < 1 or limit < 1 or limit > 50:
        return jsonify({
            "status": "error",
            "message": "Invalid query parameters"
        }), 422

    skip = (page - 1) * limit

    cursor = collection.find(filters).skip(skip).limit(limit)
    total = collection.count_documents(filters)

    data = [serialize_profile(p) for p in cursor]

    return jsonify({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": data
    }), 200
    


# ---------------------------
# DELETE
# ---------------------------

@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    result = collection.delete_one({"id": profile_id})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Profile not found"}), 404

    return "", 204


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    app.run(debug=True)