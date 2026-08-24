import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categories.schemas import CategoryCreate, CategoryUpdate
from app.core.errors import AppError
from app.models import Category


def get_category_or_404(db: Session, category_id: uuid.UUID) -> Category:
    category = db.get(Category, category_id)

    if category is None:
        raise AppError(
            code="CATEGORY_NOT_FOUND",
            message="Category not found.",
            status_code=404,
        )

    return category


def list_categories(db: Session, active_only: bool = False) -> list[Category]:
    stmt = select(Category).order_by(Category.name)

    if active_only:
        stmt = stmt.where(Category.is_active.is_(True))

    return list(db.scalars(stmt))


def ensure_name_available(
    db: Session,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> None:
    stmt = select(Category).where(Category.name == name)

    if exclude_id is not None:
        stmt = stmt.where(Category.id != exclude_id)

    if db.scalar(stmt) is not None:
        raise AppError(
            code="CATEGORY_ALREADY_EXISTS",
            message="A category with this name already exists.",
            status_code=409,
        )


def create_category(db: Session, data: CategoryCreate) -> Category:
    ensure_name_available(db, data.name.strip())

    category = Category(
        name=data.name.strip(),
        description=data.description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def update_category(
    db: Session,
    category: Category,
    data: CategoryUpdate,
) -> Category:
    changes = data.model_dump(exclude_unset=True)

    if changes.get("name") is not None:
        name = changes["name"].strip()
        ensure_name_available(db, name, exclude_id=category.id)
        category.name = name

    if "description" in changes:
        category.description = changes["description"]

    db.commit()
    db.refresh(category)

    return category


def set_category_status(
    db: Session,
    category: Category,
    is_active: bool,
) -> Category:
    category.is_active = is_active
    db.commit()
    db.refresh(category)

    return category
