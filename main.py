from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users_db = {}
reports_db = []

# MUDANÇA AQUI: O cadastro agora recebe formulário puro (Form), sem JSON!
@app.post("/signup", tags=["Usuário"])
async def create_user(username: str = Form(...), password: str = Form(...)):
    if username in users_db:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    users_db[username] = password
    # Nota: O retorno ainda é convertido pelo FastAPI, mas a ENTRADA não usa mais JSON
    return {"message": f"Usuário {username} criado com sucesso!"}

@app.post("/report", tags=["Denúncia"])
async def create_report(
    username: str = Form(...),
    password: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    date: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    if username not in users_db or users_db[username] != password:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")

    report_date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_id = f"{uuid.uuid4()}_{file.filename}"
    
    new_report = {
        "id": str(uuid.uuid4()),
        "user": username,
        "date": report_date,
        "location": location,
        "description": description,
        "image_name": file_id
    }
    reports_db.append(new_report)
    return {"message": "Denúncia registrada com sucesso!", "report": new_report}

@app.get("/reports", tags=["Denúncia"])
async def list_reports():
    return reports_db