#!/usr/bin/env python3
"""Pre-deployment health check. Run this before deploying."""
import os
import sys


def check_env_var(name: str, required: bool = True) -> bool:
    value = os.environ.get(name, "").strip()
    if not value:
        if required:
            print(f"  FAIL: {name} is not set")
            return False
        else:
            print(f"  WARN: {name} is not set (optional)")
            return True
    masked = value[:4] + "..." + value[-4:] if len(value) > 12 else "***"
    print(f"  OK: {name} = {masked}")
    return True


def main():
    print("=" * 50)
    print("B2B Stickers Deployment Health Check")
    print("=" * 50)

    all_ok = True

    print("\n[1] Required Environment Variables:")
    all_ok &= check_env_var("DATABASE_URL")
    all_ok &= check_env_var("REDIS_URL")
    all_ok &= check_env_var("JWT_SECRET")
    all_ok &= check_env_var("ADMIN_PASSWORD_HASH")
    all_ok &= check_env_var("STRIPE_SECRET_KEY")
    all_ok &= check_env_var("STRIPE_WEBHOOK_SECRET")
    all_ok &= check_env_var("STRIPE_PUBLISHABLE_KEY")

    print("\n[2] Optional Environment Variables:")
    check_env_var("REPLICATE_API_TOKEN", required=False)
    check_env_var("OPENAI_API_KEY", required=False)
    check_env_var("S3_BUCKET", required=False)
    check_env_var("PRODIGI_API_KEY", required=False)
    check_env_var("RESEND_API_KEY", required=False)

    print("\n[3] API Import Check:")
    try:
        sys.path.insert(0, "apps/api")
        os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
        from app.main import app
        print(f"  OK: API imports successfully ({len([r for r in app.routes if hasattr(r, 'methods')])} routes)")
    except Exception as e:
        print(f"  FAIL: API import error: {e}")
        all_ok = False

    print("\n[4] Security Checks:")
    jwt_secret = os.environ.get("JWT_SECRET", "")
    if len(jwt_secret) < 32:
        print(f"  WARN: JWT_SECRET is only {len(jwt_secret)} chars (recommend 32+)")
    else:
        print("  OK: JWT_SECRET is 32+ characters")

    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if not admin_hash:
        print("  FAIL: ADMIN_PASSWORD_HASH not set")
        all_ok = False
    elif not admin_hash.startswith(("$2a$", "$2b$", "$2y$")):
        print("  WARN: ADMIN_PASSWORD_HASH doesn't look like a bcrypt hash")
    else:
        print("  OK: ADMIN_PASSWORD_HASH looks valid")

    env = os.environ.get("ENV", "development")
    print(f"  OK: ENV = {env}")

    print("\n" + "=" * 50)
    if all_ok:
        print("RESULT: All checks passed. Ready to deploy!")
        return 0
    else:
        print("RESULT: Some checks failed. Fix before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
