import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.database.database import Database
from backend.database.models import Base
from backend.router import algo, babysitter, certifications, parent, requirements, users

app = FastAPI(
    debug=True,
    title="Shmartaf App",
    description="This is a simple babysitter app",
    version="0.1",
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.dependency_overrides = {
    Database: Database().get_db(),
}


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=Database().engine)


@app.get("/", include_in_schema=False)
def main():
    return RedirectResponse(url="/docs")


app.include_router(users.router)
app.include_router(babysitter.router)
app.include_router(parent.router)
app.include_router(requirements.router)
app.include_router(certifications.router)
app.include_router(algo.router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080 if os.getenv("ENV") == "local" else 80,
    )
