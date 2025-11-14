from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from app.database import donation_collection
from datetime import datetime
from enum import Enum

"""
donation module
"""


class DonationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FUNDED = "funded"
    COMPLETED = "completed"
    REJECTED = "rejected"


class DonationBase(BaseModel):
    """ class for donation model """
    food_item: str
    brand: str
    description: str
    quantity: int
    price: float
    status: DonationStatus = Field(default=DonationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DonationCreate(DonationBase):
    """ model for creating a donation """
    donor_id: str
    recipient_id: str


class Donation(DonationBase):
    """ class to represent a donation """
    id: str
    donor_id: str | None = None
    recipient_id: str

    class Config:
        """ pydantic configuration for donation """
        from_attributes = True


def donation_helper(donation) -> dict:
    """ helper function to transform donation document into dictionary """
    return {
        "id": str(donation["_id"]),
        "food_item": donation["food_item"],
        "brand": donation["brand"],
        "description": donation["description"],
        "quantity": donation["quantity"],
        "price": donation.get("price"),
        "status": donation.get("status", DonationStatus.PENDING),
        "donor_id": donation.get("donor_id"),
        "recipient_id": donation["recipient_id"],
        "created_at": donation.get("created_at"),
        "updated_at": donation.get("updated_at"),
    }


async def create_donation(donation: DonationCreate):
    """ function that creates a new donation """
    donation_dict = donation.dict()
    donation_dict["created_at"] = datetime.utcnow()
    donation_dict["updated_at"] = datetime.utcnow()
    new_donation = await donation_collection.insert_one(donation_dict)
    return donation_helper(await donation_collection.find_one({"_id": new_donation.inserted_id}))


async def get_donations(skip: int = 0, limit: int = 10):
    """ function that gets a list of donations """
    donations = await donation_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [donation_helper(donation) for donation in donations]


async def get_donation_by_id(id: str):
    """ function that gets donation by its id """
    donation = await donation_collection.find_one({"_id": ObjectId(id)})
    if donation:
        return donation_helper(donation)


async def delete_donation(id: str):
    """ function that deletes a donation by its id """
    delete_result = await donation_collection.delete_one({"_id": ObjectId(id)})
    return delete_result.deleted_count > 0


async def update_donation(id: str, donation_data: DonationBase):
    """ function that updates donation data """
    updated_data = donation_data.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.utcnow()
    update_result = await donation_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": updated_data}
    )
    if update_result.modified_count > 0:
        return await get_donation_by_id(id)
    return None


async def get_donations_by_donor_id(donor_id: str, skip: int = 0, limit: int = 10):
    """ function that gets a list of donations by donor id """
    donations = await donation_collection.find({"donor_id": donor_id}).skip(skip).limit(limit).to_list(length=limit)
    return [donation_helper(donation) for donation in donations]


async def get_donations_by_recipient_id(recipient_id: str, skip: int = 0, limit: int = 10):
    """ function that gets a list of donations by recipient id """
    donations = await donation_collection.find({"recipient_id": recipient_id}).skip(skip).limit(limit).to_list(length=limit)
    return [donation_helper(donation) for donation in donations]


async def approve_donation(id: str):
    """ function that approves a donation """
    update_result = await donation_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": DonationStatus.APPROVED, "updated_at": datetime.utcnow()}}
    )
    if update_result.modified_count > 0:
        return await get_donation_by_id(id)
    return None


async def reject_donation(id: str):
    """ function that rejects a donation """
    update_result = await donation_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": DonationStatus.REJECTED, "updated_at": datetime.utcnow()}}
    )
    if update_result.modified_count > 0:
        return await get_donation_by_id(id)
    return None


async def fund_donation(id: str, donor_id: str):
    """ function that funds a donation """
    update_result = await donation_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": DonationStatus.FUNDED, "donor_id": donor_id, "updated_at": datetime.utcnow()}}
    )
    if update_result.modified_count > 0:
        return await get_donation_by_id(id)
    return None
