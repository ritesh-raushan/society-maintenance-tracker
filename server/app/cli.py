#!/usr/bin/env python3
"""Seed CLI for Society Maintenance Tracker.

Creates initial admin user, default categories, and system settings.
"""

import getpass
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models import Category, SystemSetting, User, UserRole
from app.settings.service import DEFAULT_OVERDUE_THRESHOLD_DAYS, OVERDUE_THRESHOLD_KEY


DEFAULT_CATEGORIES = [
    "Plumbing",
    "Electrical",
    "Cleaning",
    "Security",
    "Water Supply",
    "Parking",
    "Lift",
    "Other",
]


def create_admin() -> User:
    db = SessionLocal()

    if db.scalar(select(User).where(User.role == UserRole.ADMIN)):
        print("Admin user already exists.")
        return db.scalar(select(User).where(User.role == UserRole.ADMIN))

    print("--- Create Initial Admin ---")
    name = input("Name: ").strip()
    email = input("Email: ").strip().lower()

    if not name or not email:
        print("Name and email are required.")
        sys.exit(1)

    if db.scalar(select(User).where(User.email == email)):
        print("An account with this email already exists.")
        sys.exit(1)

    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    admin = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print(f"Admin created: {admin.email} (id: {admin.id})")
    return admin


def seed_categories(db: Session) -> None:
    created = 0
    for name in DEFAULT_CATEGORIES:
        if db.scalar(select(Category).where(Category.name == name)) is None:
            db.add(Category(name=name, description=None, is_active=True))
            created += 1

    if created:
        db.commit()
        print(f"Seeded {created} categories.")
    else:
        print("All default categories already exist.")


def seed_settings(db: Session) -> None:
    if db.scalar(select(SystemSetting).where(SystemSetting.key == OVERDUE_THRESHOLD_KEY)) is None:
        db.add(
            SystemSetting(
                key=OVERDUE_THRESHOLD_KEY,
                value=str(DEFAULT_OVERDUE_THRESHOLD_DAYS),
                updated_by=None,
            ),
        )
        db.commit()
        print(f"Set {OVERDUE_THRESHOLD_KEY} = {DEFAULT_OVERDUE_THRESHOLD_DAYS}.")
    else:
        print("Overdue threshold already configured.")


def main() -> None:
    db = SessionLocal()

    try:
        create_admin()
        seed_categories(db)
        seed_settings(db)
        print("\nSeeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()