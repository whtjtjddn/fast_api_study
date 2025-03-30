from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import execute, fetch_all, fetch_one, get_db_connection
from src.models.todo import Todo
from src.schemas.todo import TodoCreate, TodoOut, TodoUpdate

router = APIRouter()


@router.get("/", response_model=list[TodoOut])
async def list_todos(conn: AsyncConnection = Depends(get_db_connection)):
    query = select(Todo)
    todos = await fetch_all(query, connection=conn)
    return todos


@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: int, conn: AsyncConnection = Depends(get_db_connection)):
    query = select(Todo).where(Todo.id == todo_id)
    todo = await fetch_one(query, connection=conn)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("/", response_model=TodoOut)
async def create_todo(
    todo: TodoCreate, conn: AsyncConnection = Depends(get_db_connection)
):
    # insert와 returning()을 이용해 생성한 행을 바로 가져옵니다.
    query = (
        insert(Todo)
        .values(
            title=todo.title, description=todo.description, completed=todo.completed
        )
        .returning(Todo)
    )
    result = await conn.execute(query)
    await conn.commit()
    created = result.first()
    if not created:
        raise HTTPException(status_code=400, detail="Creation failed")
    return created._asdict()


@router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(
    todo_id: int, todo: TodoUpdate, conn: AsyncConnection = Depends(get_db_connection)
):
    query = (
        update(Todo)
        .where(Todo.id == todo_id)
        .values(
            title=todo.title, description=todo.description, completed=todo.completed
        )
    )
    await execute(query, connection=conn, commit_after=True)
    query = select(Todo).where(Todo.id == todo_id)
    updated = await fetch_one(query, connection=conn)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@router.delete("/{todo_id}", response_model=dict)
async def delete_todo(todo_id: int, conn: AsyncConnection = Depends(get_db_connection)):
    # 삭제 전 존재 여부 확인
    query = select(Todo).where(Todo.id == todo_id)
    todo = await fetch_one(query, connection=conn)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    query = delete(Todo).where(Todo.id == todo_id)
    await execute(query, connection=conn, commit_after=True)
    return {"detail": "Todo deleted"}
