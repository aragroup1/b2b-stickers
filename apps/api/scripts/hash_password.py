#!/usr/bin/env python3
"""Generate a bcrypt hash for the admin password."""
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/hash_password.py <password>")
        print("Example: python scripts/hash_password.py my-secret-admin-pass")
        sys.exit(1)

    password = sys.argv[1]
    hashed = hash_password(password)
    print(f"\nHashed password:\n{hashed}\n")
    print(f"Set this as ADMIN_PASSWORD_HASH in your .env file")
