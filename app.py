from flask import Flask, request, jsonify
import supabase
from fcm import send_fcm_notification
from supabase import create_client
import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



SUPABASE_URL = "https://fvpmbrgjvngdktabakkw.supabase.co"
SUPABASE_KEY = "sb_publishable_oCwY3QJOU3eWWxY6LoWFfw_r2hRdkMP"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# @app.route("/vicinity-alert", methods=["POST"])
# def vicinity_alert():
#     data = request.json

#     token = data["fcm_token"]
#     sender = data["sender"]
#     message = data["message"]

#     res = send_fcm_notification(
#         token=token,
#         title="🚨 EMERGENCY ALERT",
#         body=message,
#         data={
#             "route": "/alert",
#             "sender": sender,
#             "message": message
#         }
#     )

#     return jsonify(res)

@app.route("/")
def home():
    return "Emergency Notification Service is running."

@app.route("/test", methods=["POST"])
def test_notification():
    data = request.json

    res = send_fcm_notification(
        token=data["fcm_token"],
        title="🚨 TEST ALERT",
        body="This is a test emergency notification",
        data={
            "route": "/alert",
            "sender": "SYSTEM",
            "message": "Test emergency message"
        }
    )

    return jsonify(res)

@app.route("/vicinity-alert", methods=["POST"])
def vicinity_alert():
    data = request.json

    sender_id = data["user_id"]
    sender_lat = data["latitude"]
    sender_lng = data["longitude"]
    sender_name = data["sender"]
    message = data["message"]

    RADIUS_KM = 1.5  # adjustable

    # 1️⃣ Fetch all active users
    response = (
        supabase
        .table("user_locations")
        .select("*")
        .neq("id", sender_id)
        .execute()
    )

    notified = []

    for user in response.data:
        dist = haversine(
            sender_lat,
            sender_lng,
            user["lat"],
            user["lng"]
        )
        print(f"User {user['id']} is {dist} KM away")
        if dist <= RADIUS_KM and user["fcm_token"]:
            print(f"Notifying user {user['id']} at distance {dist} KM")
            send_fcm_notification(
                token=user["fcm_token"],
                title="🚨 EMERGENCY NEAR YOU",
                body=f"{sender_name} needs help nearby!",
                data={
            "route": "/alert",
            "sender": sender_name,
            "message": message + f" (Distance: {round(dist,2)} KM)"
        }
            )

            notified.append({
                "user_id": user["id"],
                "distance_km": round(dist, 2)
            })

    return jsonify({
        "status": "ok",
        "notified_count": len(notified),
        "users": notified
    })


# if __name__ == "__main__":
#     app.run(debug=True)
