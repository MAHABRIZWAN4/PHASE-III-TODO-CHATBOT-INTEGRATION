"""Run database migration to add priority and category fields."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file in the same directory
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path, override=True)

async def run_migration():
    """Execute the migration to add priority and category columns."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please check your .env file")
        return

    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Convert postgresql:// to postgresql+asyncpg:// for async operations
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Remove sslmode and channel_binding parameters (asyncpg doesn't support them)
    # asyncpg uses ssl=require instead
    import re
    database_url = re.sub(r'[?&]sslmode=\w+', '', database_url)
    database_url = re.sub(r'[?&]channel_binding=\w+', '', database_url)

    # Add ssl=require for asyncpg
    if '?' in database_url:
        database_url += '&ssl=require'
    else:
        database_url += '?ssl=require'

    print(f"🔗 Connecting to database...")

    # Create async engine
    engine = create_async_engine(database_url, echo=True)

    try:
        async with engine.begin() as conn:
            print("\n🔄 Adding priority column...")
            await conn.execute(text("""
                ALTER TABLE tasks
                ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';
            """))

            print("\n🔄 Adding category column...")
            await conn.execute(text("""
                ALTER TABLE tasks
                ADD COLUMN IF NOT EXISTS category VARCHAR(50);
            """))

            print("\n🔄 Updating existing tasks with default priority...")
            await conn.execute(text("""
                UPDATE tasks
                SET priority = 'medium'
                WHERE priority IS NULL;
            """))

            print("\n✅ Migration completed successfully!")
            print("   - Added 'priority' column (VARCHAR(20), default: 'medium')")
            print("   - Added 'category' column (VARCHAR(50), nullable)")
            print("   - Updated existing tasks with default priority")

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
