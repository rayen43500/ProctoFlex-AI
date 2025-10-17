import os
import argparse
import getpass
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext

# Prefer PBKDF2-SHA256 (pure-python) and fall back to bcrypt if available.
# PBKDF2 avoids requiring a compiled bcrypt backend which simplifies local runs.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def get_db_url(cli_url: str | None = None) -> str:
    """Resolve the database URL.

    Priority: --db CLI -> DATABASE_URL env -> sensible local default for dev.
    """
    if cli_url:
        return cli_url
    env = os.environ.get("DATABASE_URL")
    if env:
        return env
    # sensible fallback for local dev when using docker-compose.dev.yml
    fallback = "postgresql://postgres:secure_password@localhost:5432/proctoflex"
    print(f"[warning] DATABASE_URL not set, defaulting to {fallback!r}. Use --db or set DATABASE_URL to override.")
    return fallback


def create_admin(email: str, password: str, full_name: str | None = None, is_superuser: bool = True, db_url: str | None = None):
    engine = create_engine(get_db_url(db_url), future=True)
    hashed = pwd_context.hash(password)
    now = datetime.utcnow()
    try:
        with engine.begin() as conn:
            # adapte les colonnes si ta table users a des noms différents
            r = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            if r.first():
                print(f"[skipped] user with email {email} already exists")
                return

            # detect available columns in users table and their nullability/defaults
            cols_res = conn.execute(text("SELECT column_name, is_nullable, column_default FROM information_schema.columns WHERE table_name='users'"))
            cols_meta = {row[0].lower(): {"is_nullable": row[1], "default": row[2]} for row in cols_res.fetchall()}
            available = set(cols_meta.keys())

            # candidate columns and their values
            candidates = {
                "email": email,
                "username": email.split("@")[0],
                "full_name": full_name or "",
                "hashed_password": hashed,
                "is_active": True,
                "is_superuser": is_superuser,
                "is_admin": is_superuser,
                "is_staff": is_superuser,
                "role": "admin",
                "created_at": now,
            }

            # select only those candidates that exist in the table (username first)
            insert_order = ["email", "username", "full_name", "hashed_password", "is_active", "is_superuser", "is_admin", "is_staff", "role", "created_at"]
            insert_cols = [c for c in insert_order if c in available]
            if not insert_cols:
                raise SystemExit("No known user columns found in 'users' table. Please check database schema.")

            placeholders = ", ".join([f":{c}" for c in insert_cols])
            cols_sql = ", ".join(insert_cols)
            insert_sql = text(f"INSERT INTO users ({cols_sql}) VALUES ({placeholders})")

            # ensure required NOT NULL columns have values; provide sensible defaults
            params = {c: candidates.get(c) for c in insert_cols}
            # Ensure username uniqueness if present
            if "username" in insert_cols:
                desired = params.get("username") or email.split("@")[0]
                base = desired
                i = 0
                while True:
                    uq = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": desired})
                    if not uq.first():
                        params["username"] = desired
                        break
                    i += 1
                    desired = f"{base}{i}"
            for col in insert_cols:
                meta = cols_meta.get(col, {})
                is_nullable = (meta.get("is_nullable") or "YES").upper() == "YES"
                default = meta.get("default")
                if (params.get(col) is None) and (not is_nullable) and (default is None):
                    # provide sane defaults for common required fields
                    if col == "username":
                        params[col] = email.split("@")[0]
                    elif col in ("full_name", "name"):
                        params[col] = full_name or ""
                    elif col in ("hashed_password", "password"):
                        params[col] = hashed
                    elif col in ("is_active", "active"):
                        params[col] = True
                    elif col in ("is_superuser", "is_admin", "is_staff"):
                        params[col] = is_superuser
                    elif col == "role":
                        params[col] = "admin"
                    elif col.endswith("_at") or col in ("created_at", "createdon"):
                        params[col] = now
                    else:
                        # fallback: empty string
                        params[col] = ""
            conn.execute(insert_sql, params)
            print(f"[ok] created admin {email} (inserted columns: {', '.join(insert_cols)})")
    except SQLAlchemyError as exc:
        print("[error] database operation failed:", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Create an admin user in the database. If email/password are omitted, you'll be prompted.")
    p.add_argument("--email", required=False, help="Admin email")
    p.add_argument("--password", required=False, help="Admin password")
    p.add_argument("--name", default="", help="Full name")
    p.add_argument("--db", dest="db_url", required=False, help="Database URL (overrides DATABASE_URL env)")
    # allow explicit toggling of superuser flag
    p.add_argument("--super", dest="is_super", action="store_true", help="mark user as superuser")
    p.add_argument("--no-super", dest="is_super", action="store_false", help="do not mark as superuser")
    p.set_defaults(is_super=True)
    args = p.parse_args()

    email = args.email or input("Email: ").strip()
    if not email:
        raise SystemExit("Email is required")
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")
        if not password:
            raise SystemExit("Password is required")

    create_admin(email, password, full_name=args.name, is_superuser=bool(args.is_super), db_url=args.db_url)