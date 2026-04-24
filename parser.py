import re

def parse_query(q: str):
    q = q.lower()
    query = {}    

    # -------------------
    # GENDER (FIXED)
    # -------------------
    has_male = re.search(r"\bmale(s)?\b", q)
    has_female = re.search(r"\bfemale(s)?\b", q)

    if has_female and has_male:
        pass
    elif has_female:
        query["gender"] = "female"
    elif has_male:
        query["gender"] = "male"

    # -------------------
    # AGE (FIXED)
    # -------------------
    age_filter = {}

    # young → 16–24
    if "young" in q:
        age_filter["$gte"] = 16
        age_filter["$lte"] = 24

    # above X
    match = re.search(r"above (\d+)", q)
    if match:
        age_filter["$gte"] = int(match.group(1))

    if age_filter:
        query["age"] = age_filter

    # -------------------
    # AGE GROUP
    # -------------------
    if "child" in q:
        query["age_group"] = "child"
    elif "teenager" in q:
        query["age_group"] = "teenager"
    elif "adult" in q:
        query["age_group"] = "adult"
    elif "senior" in q:
        query["age_group"] = "senior"

    # -------------------
    # COUNTRY
    # -------------------
    country_map = {
        "nigeria": "NG",
        "kenya": "KE",
        "angola": "AO",
        "ghana": "GH",
        "tanzania": "TZ"
    }

    for name, code in country_map.items():
        if name in q:
            query["country_id"] = code
            break

    # -------------------
    # VALIDATION
    # -------------------
    if not query:
        return None

    return query