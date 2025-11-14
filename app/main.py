from fastapi import FastAPI
from app.routes import donations, user, donor, recipient, reviews, volunteer, auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi_standalone_docs import StandaloneDocs


app = FastAPI(
    title="Food Donation API",
    description="API for managing food donations,users, donors, recipients, community volunteers and reviews",
    version="1.0.0",
)

StandaloneDocs(app=app)

""" Enable CORS """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow requests from any origin, change in production
    allow_credentials=True, # Allow cookies and authentication headers
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"], # Allow all HTTP headers
)

""" routes from other modules"""
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(donor.router)
app.include_router(donations.router)
app.include_router(recipient.router)
app.include_router(volunteer.router)
app.include_router(reviews.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
