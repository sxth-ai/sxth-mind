"""
SQLite Storage

SQLite-based storage implementation. Data persists across restarts.
"""

from pathlib import Path
from uuid import uuid4

from sxth_mind.schemas import ConversationMemory, Nudge, ProjectMind, UserMind
from sxth_mind.storage.base import BaseStorage


class SQLiteStorage(BaseStorage):
    """
    SQLite storage implementation.

    Stores all data in a SQLite database. Persists across restarts.

    Requires: pip install sxth-mind[sqlite]

    Usage:
        from sxth_mind.storage import SQLiteStorage

        storage = SQLiteStorage("mind.db")
        mind = Mind(adapter=MyAdapter(), storage=storage)
    """

    def __init__(self, db_path: str = "sxth_mind.db"):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._conn = None

    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        try:
            import aiosqlite
        except ImportError:
            raise ImportError(
                "aiosqlite not installed. Install with:\n"
                "  pip install sxth-mind[sqlite]"
            )

        self._conn = await aiosqlite.connect(self.db_path)

        # Create tables
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_minds (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS project_minds (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                user_mind_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, project_id)
            );

            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                project_mind_id TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS nudges (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_mind_id TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_user_minds_user_id ON user_minds(user_id);
            CREATE INDEX IF NOT EXISTS idx_project_minds_user_id ON project_minds(user_id);
            CREATE INDEX IF NOT EXISTS idx_nudges_user_id ON nudges(user_id);
            CREATE INDEX IF NOT EXISTS idx_nudges_status ON nudges(status);
        """)
        await self._conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    def _ensure_connected(self) -> None:
        if self._conn is None:
            raise RuntimeError("Storage not initialized. Call initialize() first.")

    # ═══════════════════════════════════════════════════════════════
    # UserMind Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_user_mind(self, user_id: str) -> UserMind | None:
        self._ensure_connected()

        async with self._conn.execute(
            "SELECT data FROM user_minds WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserMind.model_validate_json(row[0])
            return None

    async def save_user_mind(self, user_mind: UserMind) -> None:
        self._ensure_connected()

        if not user_mind.id:
            user_mind.id = str(uuid4())

        data = user_mind.model_dump_json()
        now = user_mind.updated_at.isoformat()

        await self._conn.execute("""
            INSERT INTO user_minds (id, user_id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                data = excluded.data,
                updated_at = excluded.updated_at
        """, (user_mind.id, user_mind.user_id, data, now, now))
        await self._conn.commit()

    async def delete_user_mind(self, user_id: str) -> None:
        self._ensure_connected()

        # Delete related data first
        await self._conn.execute(
            "DELETE FROM project_minds WHERE user_id = ?", (user_id,)
        )
        await self._conn.execute(
            "DELETE FROM nudges WHERE user_id = ?", (user_id,)
        )
        await self._conn.execute(
            "DELETE FROM user_minds WHERE user_id = ?", (user_id,)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════════
    # ProjectMind Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_project_mind(
        self, user_id: str, project_id: str
    ) -> ProjectMind | None:
        self._ensure_connected()

        async with self._conn.execute(
            "SELECT data FROM project_minds WHERE user_id = ? AND project_id = ?",
            (user_id, project_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return ProjectMind.model_validate_json(row[0])
            return None

    async def save_project_mind(self, project_mind: ProjectMind) -> None:
        self._ensure_connected()

        if not project_mind.id:
            project_mind.id = str(uuid4())

        # Get user_id from user_mind
        async with self._conn.execute(
            "SELECT user_id FROM user_minds WHERE id = ?",
            (project_mind.user_mind_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"UserMind {project_mind.user_mind_id} not found")
            user_id = row[0]

        data = project_mind.model_dump_json()
        now = project_mind.updated_at.isoformat()

        await self._conn.execute("""
            INSERT INTO project_minds (id, user_id, project_id, user_mind_id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, project_id) DO UPDATE SET
                data = excluded.data,
                updated_at = excluded.updated_at
        """, (project_mind.id, user_id, project_mind.project_id, project_mind.user_mind_id, data, now, now))
        await self._conn.commit()

    async def get_project_minds_for_user(self, user_id: str) -> list[ProjectMind]:
        self._ensure_connected()

        async with self._conn.execute(
            "SELECT data FROM project_minds WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [ProjectMind.model_validate_json(row[0]) for row in rows]

    async def delete_project_mind(self, user_id: str, project_id: str) -> None:
        self._ensure_connected()

        # Get project_mind_id first
        async with self._conn.execute(
            "SELECT id FROM project_minds WHERE user_id = ? AND project_id = ?",
            (user_id, project_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                pm_id = row[0]
                # Delete related memory
                await self._conn.execute(
                    "DELETE FROM memories WHERE project_mind_id = ?", (pm_id,)
                )

        await self._conn.execute(
            "DELETE FROM project_minds WHERE user_id = ? AND project_id = ?",
            (user_id, project_id)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════════
    # ConversationMemory Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_memory(self, project_mind_id: str) -> ConversationMemory | None:
        self._ensure_connected()

        async with self._conn.execute(
            "SELECT data FROM memories WHERE project_mind_id = ?",
            (project_mind_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return ConversationMemory.model_validate_json(row[0])
            return None

    async def save_memory(self, memory: ConversationMemory) -> None:
        self._ensure_connected()

        if not memory.id:
            memory.id = str(uuid4())

        data = memory.model_dump_json()
        now = memory.updated_at.isoformat()

        await self._conn.execute("""
            INSERT INTO memories (id, project_mind_id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_mind_id) DO UPDATE SET
                data = excluded.data,
                updated_at = excluded.updated_at
        """, (memory.id, memory.project_mind_id, data, now, now))
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════════
    # Nudge Operations
    # ═══════════════════════════════════════════════════════════════

    async def get_pending_nudges(self, user_id: str) -> list[Nudge]:
        self._ensure_connected()

        async with self._conn.execute(
            "SELECT data FROM nudges WHERE user_id = ? AND status = 'pending'",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [Nudge.model_validate_json(row[0]) for row in rows]

    async def save_nudge(self, nudge: Nudge) -> None:
        self._ensure_connected()

        if not nudge.id:
            nudge.id = str(uuid4())

        # Get user_id from project_mind
        async with self._conn.execute(
            "SELECT user_id FROM project_minds WHERE id = ?",
            (nudge.project_mind_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"ProjectMind {nudge.project_mind_id} not found")
            user_id = row[0]

        data = nudge.model_dump_json()
        now = nudge.updated_at.isoformat()

        await self._conn.execute("""
            INSERT INTO nudges (id, user_id, project_mind_id, data, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                data = excluded.data,
                status = excluded.status,
                updated_at = excluded.updated_at
        """, (nudge.id, user_id, nudge.project_mind_id, data, nudge.status, now, now))
        await self._conn.commit()
