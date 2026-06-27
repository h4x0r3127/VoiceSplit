import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export, ExportStatus
from app.repositories.base import BaseRepository


class ExportRepository(BaseRepository[Export]):
    def __init__(self) -> None:
        super().__init__(Export)

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Export], int]:
        query = select(Export).where(
            Export.user_id == user_id,
            Export.deleted_at.is_(None),
        )
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await db.execute(
            query.order_by(Export.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def update_status(
        self,
        db: AsyncSession,
        export_id: uuid.UUID,
        status: ExportStatus,
        output_s3_key: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Export]:
        values: dict = {"status": status}
        if output_s3_key is not None:
            values["output_s3_key"] = output_s3_key
        if error_message is not None:
            values["error_message"] = error_message

        await db.execute(
            update(Export).where(Export.id == export_id).values(**values)
        )
        await db.flush()
        return await self.get_by_id(db, export_id)
