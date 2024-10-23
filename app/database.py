from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB conncetion details
MONGO_DETAILS = "mongodb://sustainashareadmin:Mally#13@localhost:27017/sustainashare"

# Establish connection to MongoDB server
client = AsyncIOMotorClient(MONGO_DETAILS)

# Initialize database
database = client.sustainashare

# Initialize collections for storing data
donor_collection = database.get_collection("donors")
recipient_collection = database.get_collection("recipients")
donation_collection = database.get_collection("donations")
user_collection = database.get_collection("users")
volunteer_collection = database.get_collection("volunteers")
review_collection = database.get_collection("reviews")
