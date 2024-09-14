from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from model import User, Client
from auth import get_current_user
from schemas import ClientResponse, ClientCreate
from database import get_db
from uuid import UUID

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

@router.post("/", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_client = Client(full_name=client.full_name, phone_number=client.phone_number, user_id=current_user.id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client



@router.get('/', response_model=list[ClientResponse])
def get_clients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Client).filter(Client.user_id == current_user.id).all()


@router.get('/{client_id}', response_model=ClientResponse)
async def get_client(client_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Client).filter(Client.id == client_id, Client.user_id == current_user.id).first()

@router.put('/{client_id}', response_model=ClientResponse)
async def update_client(client_id: UUID, update_client: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    client = db.query(Client).filter( Client.id == client_id, Client.user_id == current_user.id).first()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details='client not found or anuthorize access')

    client.full_name = update_client.full_name
    client.phone_number = update_client.phone_number


    db.commit()
    db.refresh(client)

    return client


@router.delete('/{client_id}', response_model=dict)
async def delete_client(client_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    client = db.query(Client).filter( Client.id == client_id, Client.user_id == current_user.id).first()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details='client not found or anuthorize access')

    db.delete(client)
    db.commit()

    return {'msg': 'client deleted successfully'}