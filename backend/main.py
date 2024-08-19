from typing import List
import fastapi
import fastapi.security as security
import sqlalchemy.orm as orm
import services 
import schemas

app = fastapi.FastAPI()

@app.post("/api/users")
async def create_user(user: schemas.UserCreate, db: orm.Session = fastapi.Depends(services.get_db)):
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Email already registered")
    
    await services.create_user(user, db)
    
    return await services.create_token(user) 

@app.post("/api/token")
async def generate_token(form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(), db: orm.Session = fastapi.Depends(services.get_db)):
    user = await services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")
    
    return await services.create_token(user)

@app.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user

@app.post("/api/leads", response_model=schemas.Lead)
async def create_lead(lead: schemas.LeadCreate, user: schemas.User = fastapi.Depends(services.get_current_user), db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.create_lead(user=user, db=db, lead=lead)

@app.get("/api/leads", response_model=List[schemas.Lead])
async def get_leads(user: schemas.User = fastapi.Depends(services.get_current_user), db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.get_leads(user=user, db=db)

@app.get("/api/leads/{lead_id}", status_code=200)
async def get_lead(lead_id: int, user: schemas.User = fastapi.Depends(services.get_current_user), db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.get_lead(lead_id=lead_id, user=user, db=db)

@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, user: schemas.User = fastapi.Depends(services.get_current_user), db: orm.Session = fastapi.Depends(services.get_db)):
    await services.delete_lead(lead_id=lead_id, user=user, db=db)
    return {"message", "Successfully deleted lead"}

@app.put("/api/leads/{lead_id}", status_code=200)
async def update_lead(lead_id: int, lead: schemas.LeadCreate, user: schemas.User = fastapi.Depends(services.get_current_user), db: orm.Session = fastapi.Depends(services.get_db)):
    await services.update_lead(lead_id, lead, user, db)
    return {"message", "Successfully updated lead"}