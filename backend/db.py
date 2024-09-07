import motor.motor_asyncio
from bson.objectid import ObjectId

MONGO_DETAILS = "mongodb+srv://... replace with your own"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.csapp

user_collection = database.get_collection("users")


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "hashed_password": user["hashed_password"],
        "role": user.get("role", "user"),
        "is_activated": user.get("is_activated", False),
    }
