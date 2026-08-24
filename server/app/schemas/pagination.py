from math import ceil
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def pagination_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> tuple[int, int]:
    return page, page_size


def run_paginated_query(
    db: Session,
    stmt: Select,
    page: int,
    page_size: int,
) -> tuple[list, int]:
    total = db.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )

    items = list(
        db.scalars(
            stmt.limit(page_size).offset((page - 1) * page_size),
        ),
    )

    return items, total or 0


def build_page(items: list[T], total: int, page: int, page_size: int) -> Page[T]:
    return Page[T](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )
