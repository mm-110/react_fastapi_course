import database
import models
import schemas
import sqlalchemy.orm as orm
import fastapi
import fastapi.security as security

import passlib.hash as hash
import jwt

import datetime as dt

oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "myjwtsecret" # questo va inserito in un .env

def create_database():
    return database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_email(email: str, db: orm.Session):
    return db.query(models.User).filter(models.User.email == email).first()

async def create_user(user: schemas.UserCreate, db: orm.Session):
    user_obj = models.User(email=user.email, hashed_password=hash.bcrypt.hash(user.hashed_password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email: str, password: str, db: orm.Session):
    user = await get_user_by_email(email=email, db=db)

    if not user:
        return False
    
    if not user.verify_password(password):
        return False

    return user

async def create_token(user: models.User):
    user_obj = schemas.User.from_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type='bearer')

async def get_current_user(db: orm.Session = fastapi.Depends(get_db), token: str = fastapi.Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload['id'])
    except:
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")
    
    return schemas.User.from_orm(user)

async def create_lead(user: schemas.User, db: orm.Session, lead: schemas.LeadCreate):
    lead = models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return schemas.Lead.from_orm(lead)

async def get_leads(user: schemas.User, db: orm.Session):
    leads = db.query(models.Lead).filter(models.Lead.owner_id == user.id).all()
    return list(map(schemas.Lead.from_orm, leads))

async def lead_selector(lead_id: int, user: schemas.User, db: orm.Session):
    lead = (db.query(models.Lead).filter(models.Lead.owner_id == user.id, models.Lead.id == lead_id).first())
    if not lead:
        raise fastapi.HTTPException(status_code=404, detail="Lead not found")
    return lead

async def get_lead(lead_id: int, user: schemas.User, db: orm.Session):
    lead = await lead_selector(lead_id, user, db)
    return schemas.Lead.from_orm(lead)

async def delete_lead(lead_id: int, user: schemas.User, db: orm.Session):
    lead = await lead_selector(lead_id, user, db)
    db.delete(lead)
    db.commit()
    # return schemas.Lead.from_orm(lead)

async def update_lead(lead_id: int, lead: schemas.LeadCreate, user: schemas.User, db: orm.Session):
    lead_db = await lead_selector(lead_id, user, db)
    
    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_update = dt.datetime.now()

    db.commit()
    db.refresh(lead_db)

    return schemas.Lead.from_orm(lead_db)



