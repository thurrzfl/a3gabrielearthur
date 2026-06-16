
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uuid

# Importações do SQLAlchemypython 
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ---- CONFIGURAÇÃO DO BANCO DE DADOS ----
DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---- MODELOS DO BANCO DE DADOS (TABELAS) ----
class UserTable(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)

class ReportTable(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, index=True)
    user = Column(String, nullable=False)
    date = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_name = Column(String, nullable=False)

# Cria as tabelas no arquivo database.db caso elas não existam
Base.metadata.create_all(bind=engine)

# ---- INICIALIZAÇÃO DO FASTAPI ----
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência para obter a sessão do banco de dados em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- ROTAS (ENDPOINTS) ----

@app.post("/signup", tags=["Usuário"])
async def create_user(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Busca se o usuário já existe no banco
    user_exists = db.query(UserTable).filter(UserTable.username == username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    
    # Cria o novo usuário
    new_user = UserTable(username=username, password=password)
    db.add(new_user)
    db.commit() # Salva no banco de dados
    
    return {"message": f"Usuário {username} criado com sucesso!"}

@app.post("/report", tags=["Denúncia"])
async def create_report(
    username: str = Form(...),
    password: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verifica as credenciais direto no banco de dados
    user = db.query(UserTable).filter(UserTable.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")

    report_date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_id = f"{uuid.uuid4()}_{file.filename}"
    report_id = str(uuid.uuid4())
    
    # Cria o objeto da denúncia
    new_report = ReportTable(
        id=report_id,
        user=username,
        date=report_date,
        location=location,
        description=description,
        image_name=file_id
    )
    
    db.add(new_report)
    db.commit() # Salva no banco de dados
    db.refresh(new_report) # Atualiza o objeto com os dados do banco
    
    return {
        "message": "Denúncia registrada com sucesso!", 
        "report": {
            "id": new_report.id,
            "user": new_report.user,
            "date": new_report.date,
            "location": new_report.location,
            "description": new_report.description,
            "image_name": new_report.image_name
        }
    }

@app.get("/reports", tags=["Denúncia"])
async def list_reports(db: Session = Depends(get_db)):
    # Busca todas as denúncias cadastradas
    reports = db.query(ReportTable).all()
    return reports