from typing import Any, Sequence

from sqlalchemy import Row, RowMapping, Select
from sqlalchemy.ext.asyncio import AsyncSession


class Pagination:
    def __init__(
        self, session: AsyncSession, query: Select, page: int = 1, page_size: int = 10
    ):
        self.session = session
        self.query = query
        self.page = page
        self.page_size = page_size

    async def fetch_results(self) -> Sequence[Row[Any] | RowMapping | Any]:
        offset = (self.page - 1) * self.page_size
        query = self.query.offset(offset).limit(self.page_size)
        results = await self.session.execute(query)
        return results.scalars().all()
