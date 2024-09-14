from fastapi import FastAPI
from user import router as user_router
from client import router as client_router
from message import router as message_router
from auth import router as auth_router
from database import Base, engine
# from .routers import user, clients, messages


Base.metadata.create_all(engine)
app = FastAPI()

app.include_router(user_router)
app.include_router(client_router)
app.include_router(message_router)
app.include_router(auth_router)

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Bulk SMS API is running"}
