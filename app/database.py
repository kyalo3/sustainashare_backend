from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB conncetion details
MONGO_DETAILS = "mongodb+srv://kyalo:root@cluster0.trlij3n.mongodb.net/FoodDonation?retryWrites=true&w=majority"

# Establish connection to MongoDB server
client = AsyncIOMotorClient(MONGO_DETAILS)

# Initialize database
database = client.FoodDonation

# Initialize collections for storing data
donor_collection = database.get_collection("donors")
recipient_collection = database.get_collection("recipients")
donation_collection = database.get_collection("donations")
user_collection = database.get_collection("users")
volunteer_collection = database.get_collection("volunteers")
review_collection = database.get_collection("reviews")
