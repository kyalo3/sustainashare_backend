from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.volunteer import Volunteer, VolunteerCreate, VolunteerUpdate, create_volunteer, get_volunteer_by_id
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/volunteers/", response_model=Volunteer)
async def create_volunteer_endpoint(volunteer: VolunteerCreate, current_user: User = Depends(get_current_user)):
    """creates a new volunteer, allows a volunteer user to create a new
    by probiding necessary volunteer data
    Args:
        volunteer: volunteer data to be created
        current_user: current logged_in user, obtained through dependency
        injection
    Returns:
        dict: a dictionary containing the created volunteer's details.
    Raises:
        HTTPException: if there is an error in volunteer creation
    """
    volunteer = await create_volunteer(volunteer, user_id=current_user["id"])

    return {"id": volunteer.get("id"), "name": volunteer.get("name"), "user_id": current_user["id"]}

@router.get("/volunteers/{volunteer_id}", response_model=Volunteer)
async def get_volunteer_endpoint(volunteer_id: str):
    """gets a volunteer by id
    Args:
        volunteer_id: id of the volunteer to be fetched
    Returns:
        dict: a dictionary containing the volunteer's details.
    Raises:
        HTTPException: if the volunteer is not found
    """
    volunteer = await get_volunteer_by_id(volunteer_id)
    if volunteer:
        return volunteer
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Volunteer with id {volunteer_id} not found")

@router.get("/volunteers/", response_model=List[Volunteer])
async def get_volunteers_endpoint(current_user: User = Depends(get_current_user)):
    """gets all volunteers
    Args:
        current_user: current logged_in user, obtained through dependency
        injection
    Returns:
        list: a list containing dictionaries of all volunteers
    """
    volunteers = await get_volunteer_by_user_id(current_user["id"])
    return volunteers

@router.put("/volunteers/{volunteer_id}", response_model=Volunteer)
async def update_volunteer_endpoint(volunteer_id: str, volunteer: VolunteerUpdate):
    """updates a volunteer by id
    Args:
        volunteer_id: id of the volunteer to be updated
        volunteer: updated volunteer data
    Returns:
        dict: a dictionary containing the updated volunteer's details.
    Raises:
        HTTPException: if the volunteer is not found
    """
    updated_volunteer = await update_volunteer(volunteer_id, volunteer)
    if updated_volunteer:
        return updated_volunteer
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Volunteer with id {volunteer_id} not found")

@router.delete("/volunteers/{volunteer_id}", response_model=dict)
async def delete_volunteer_endpoint(volunteer_id: str):
    """deletes a volunteer by id
    Args:
        volunteer_id: id of the volunteer to be deleted
    Returns:
        dict: a dictionary containing the deleted volunteer's details.
    Raises:
        HTTPException: if the volunteer is not found
    """
    deleted_volunteer = await delete_volunteer(volunteer_id)
    if deleted_volunteer:
        return {"message": f"Volunteer with id {volunteer_id} deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Volunteer with id {volunteer_id} not found")

# Path: app/routes/recipient.py
