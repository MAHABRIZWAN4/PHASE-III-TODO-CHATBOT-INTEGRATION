import asyncio
from sqlmodel import select
from models import Task
from db import async_session_maker

async def check_tasks():
    async with async_session_maker() as session:
        result = await session.exec(select(Task).limit(5))
        tasks = result.all()
        
        print("\n=== First 5 Tasks in Database ===")
        for task in tasks:
            print(f"ID: {task.id}, Title: {task.title}, User ID: {task.user_id}")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(check_tasks())
