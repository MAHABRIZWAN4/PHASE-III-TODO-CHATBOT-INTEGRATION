import asyncio
from mcp_server.task_tools import list_tasks

async def test():
    # Test with the user's actual user_id
    result = await list_tasks(
        user_id="a6028fe8-e47b-4c95-ad91-32b34ba3e5dc",
        status="all",
        limit=100
    )
    
    print("\n=== list_tasks Result ===")
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    print("\nTasks:")
    for task in result.get('tasks', []):
        print(f"  ID: {task['id']}, Title: {task['title']}, User: {task['user_id']}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())
