# Todo API

FastAPI + PostgreSQL + Docker で構築したREST API。JWT認証付き。

## 使用技術

- Python / FastAPI
- PostgreSQL
- SQLAlchemy
- Docker / Docker Compose
- JWT認証

## 起動方法
```bash
docker-compose up --build
```

起動後、以下のURLでSwagger UIにアクセスできます：
http://localhost:8000/docs

## APIエンドポイント

| メソッド | パス | 説明 | 認証 |
|--------|------|------|------|
| POST | /register | ユーザー登録 | 不要 |
| POST | /login | ログイン・トークン取得 | 不要 |
| GET | /todos | Todo一覧取得 | 必要 |
| POST | /todos | Todo追加 | 必要 |
| PATCH | /todos/{id}/done | 完了フラグ切り替え | 必要 |
| DELETE | /todos/{id} | Todo削除 | 必要 |