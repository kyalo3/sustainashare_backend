from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.reviews import Review, ReviewCreate, create_review, get_reviews_by_user_id, update_review
from app.models.user import get_user_by_email  # Assuming this function exists

router = APIRouter()

@router.post("/reviews/", response_model=Review)
async def register_review(review: ReviewCreate):
    """
    This endpoint allows users to create a review.
    Request Body:
        title: title of the review
        content: content of the review
        rating: rating of the review
        email: email of the user creating the review
    """
    user = await get_user_by_email(review.email)  # Fetch user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    review_id = await create_review(review)
    return {
        "id": review_id,
        "title": review.title,
        "content": review.content,
        "rating": review.rating,
        "email": review.email  # Return email instead of user_id
    }

@router.get("/reviews/user/{email}", response_model=List[Review])
async def get_user_reviews(email: str):
    """
    This endpoint allows users to fetch reviews by user email.
    Path Parameter:
        email: email of the user
    """
    user = await get_user_by_email(email)  # Fetch user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reviews = await get_reviews_by_user_id(user["id"])  # Fetch reviews using the user ID from the fetched user
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this user")
    return reviews

@router.put("/reviews/{review_id}", response_model=Review)
async def update_review_endpoint(review_id: str, review: ReviewCreate):
    """
    This endpoint allows users to update a review.
    Path Parameter:
        review_id: id of the review to be updated
    Request Body:
        title: updated title of the review
        content: updated content of the review
        rating: updated rating of the review
        email: email of the user updating the review
    """
    user = await get_user_by_email(review.email)  # Fetch user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_review = await get_review_by_id(review_id)  # Fetch the review by ID
    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Ensure the user trying to update the review is the owner
    if existing_review["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You do not have permission to update this review")

    updated_review = await update_review(review_id, review)
    if not updated_review:
        raise HTTPException(status_code=500, detail="Failed to update review")
    
    return updated_review

# @router.delete("/reviews/{review_id}", response_model=dict)
# async def delete_review_endpoint(review_id: str):
#     """
#     This endpoint allows users to delete a review.
#     Path Parameter:
#         review_id: id of the review to be deleted
#     """
#     deleted_review = await delete_review(review_id)
#     if not deleted_review:
#         raise HTTPException(status_code=500, detail="Failed to delete review")
    
#     return {"message": "Review deleted successfully"}
