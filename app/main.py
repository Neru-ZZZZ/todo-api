from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from auth import verify_password, get_password_hash, create_access_token, decode_access_token

# テーブルを自動作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# スキーマ
class TodoCreate(BaseModel):
    item: str

class UserCreate(BaseModel):
    username: str
    password: str

# 現在のユーザーを取得
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="認証エラー")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="認証エラー")
    return user

# ユーザー登録
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="すでに登録されています")
    hashed = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return {"message": "登録しました"}

# ログイン
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが違います")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# 一覧取得
@app.get("/todos")
def get_todos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Todo).all()

# 追加
@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = models.Todo(item=todo.item)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return {"message": "追加しました", "todo": db_todo}

# 完了フラグを切り替える
@app.patch("/todos/{todo_id}/done")
def toggle_done(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="見つかりませんでした")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return {"message": "更新しました", "todo": todo}

# 削除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="見つかりませんでした")
    db.delete(todo)
    db.commit()
    return {"message": "削除しました", "todo": todo}