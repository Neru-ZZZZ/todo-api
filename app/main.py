from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# テーブルを自動作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# リクエスト用のスキーマ
class TodoCreate(BaseModel):
    item: str

# 一覧取得
@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# 追加
@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(item=todo.item)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return {"message": "追加しました", "todo": db_todo}

# 完了フラグを切り替える
@app.patch("/todos/{todo_id}/done")
def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="見つかりませんでした")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return {"message": "更新しました", "todo": todo}

# 削除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="見つかりませんでした")
    db.delete(todo)
    db.commit()
    return {"message": "削除しました", "todo": todo}