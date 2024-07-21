import sys
import asyncio
from pathlib import Path
from app.db import engine
from app.models import Base

sys.path.append(str(Path(__file__).resolve().parent.parent))


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Only run init_db if this script is executed directly (to avoid running it during imports)
if __name__ == "__main__":
    asyncio.run(init_db())
