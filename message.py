from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import os
import requests
from dotenv import load_dotenv
from schemas import MessageCreate, MessageResponse, SentMessageCreate
from database import get_db
from auth import get_current_user
from uuid import UUID
from model import Message, User, Client, MessageStatus # MessageStatus is a schema in model



load_dotenv()

ARKESEL_API_KEY = os.getenv("ARKESEL_API_KEY")
ARKESEL_URL = os.getenv("ARKESEL_URL")
SENDER_ID = os.getenv("SENDER_ID")

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

arkesel_client = requests.Session()

arkesel_action = "send-sms"


@router.post("/", response_model=list[MessageResponse])
async def send_message(inputs: SentMessageCreate, background_task: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sent_messages: list[MessageCreate] = []
    for c_id in inputs.clients:
        db_message = Message(content=inputs.content, client_id=c_id, user_id=current_user.id)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        sent_messages.append(db_message)
    
    background_task.add_task(send_sms_in_background, sent_messages, db)
    return sent_messages


@router.get("/")
async def get_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Message).filter(Message.user_id == current_user.id).all()


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Message).filter(Message.id == message_id, Message.user_id == current_user.id).first()


@router.delete("/{message_id}")
async def delete_message(message_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_message = db.query(Message).filter(Message.id == message_id, Message.user_id == current_user.id).first()

    db.delete(db_message)
    db.commit()

    return {"msg": "Message deleted successfully"}


def send_sms_in_background(messages: list[MessageCreate], db: Session):

    for message in messages:
        # Get each message from the database
        db_message = db.query(Message).filter(Message.id == message.id).first()
        if not db_message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Get individual client to send messages to
        db_client = db.query(Client).filter(Client.id == message.client_id).first()
        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found!")


        try:
            # Send SMS using the prefered api 
            url = "https://sms.arkesel.com/sms/api"
            params = {
                "action": "send-sms",
                "api_key": ARKESEL_API_KEY,
                "to": db_client.phone_number,
                "from": SENDER_ID,
                "sms": str(db_message.content)
            }

            print(params)
            print("=================FIRST=======================")
           

            # Send HTTP GET request
            try:
                response = arkesel_client.get(url, params=params)
                response.raise_for_status()
                print(response.text)
            except requests.exceptions.RequestException as e:
                print("An error occurred:", e)
            
            
            # Update the message status to 'sent'
            db_message.status = MessageStatus.SENT
            db.commit()
            db.refresh(db_message)
        except Exception as e:
            # Update the message status to 'failed' if sending fails
            db_message.status = MessageStatus.FAILED
            db.commit()
            db.refresh(db_message)



