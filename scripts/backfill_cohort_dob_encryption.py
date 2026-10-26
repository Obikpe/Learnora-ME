#!/usr/bin/env python3
"""Backfill cohort DOBs to application-encrypted storage.

Safe by default: without --apply this script only reports how many rows would
change. It never prints dates of birth or encryption keys. Run from a trusted
operator workstation with SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and
COHORT_DOB_ENCRYPTION_KEY set. Do not run against production until the owner
has approved the maintenance window and backed up the affected rows.
"""
import argparse
import os
import sys
from datetime import date
from cryptography.fernet import Fernet
from supabase import create_client


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write encrypted values and clear plaintext DOBs")
    parser.add_argument("--page-size", type=int, default=500, help="read page size (default: 500)")
    args = parser.parse_args()
    if args.page_size < 1 or args.page_size > 2000:
        parser.error("--page-size must be between 1 and 2000")

    url = os.getenv("SUPABASE_URL", "").strip()
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    encryption_key = os.getenv("COHORT_DOB_ENCRYPTION_KEY", "").strip()
    if not url or not service_key or not encryption_key:
        print("Missing SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, or COHORT_DOB_ENCRYPTION_KEY.", file=sys.stderr)
        return 2
    try:
        cipher = Fernet(encryption_key.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        print("COHORT_DOB_ENCRYPTION_KEY is not a valid Fernet key.", file=sys.stderr)
        return 2

    db = create_client(url, service_key)
    rows = []
    offset = 0
    while True:
        page = (
            db.table("cohort_accounts")
            .select("id,date_of_birth,date_of_birth_encrypted")
            .not_.is_("date_of_birth", "null")
            .order("id")
            .range(offset, offset + args.page_size - 1)
            .execute()
        ).data or []
        rows.extend(page)
        if len(page) < args.page_size:
            break
        offset += len(page)

    print(f"Plaintext DOB rows found: {len(rows)}")
    if not args.apply:
        print("Dry run only. No rows were changed. Re-run with --apply after approval.")
        return 0

    changed = 0
    for row in rows:
        raw = str(row.get("date_of_birth") or "").strip()
        if not raw:
            continue
        try:
            normalized = date.fromisoformat(raw[:10]).isoformat()
        except ValueError:
            print(f"Stopped: row {row.get('id')} has an unparseable DOB; no value was logged.", file=sys.stderr)
            return 1
        encrypted = cipher.encrypt(normalized.encode("ascii")).decode("ascii")
        updated = (
            db.table("cohort_accounts")
            .update({"date_of_birth_encrypted": encrypted, "date_of_birth": None})
            .eq("id", row["id"])
            .eq("date_of_birth", raw)
            .select("id")
            .execute()
        ).data or []
        if not updated:
            print(f"Stopped: row {row.get('id')} changed concurrently; review before retrying.", file=sys.stderr)
            return 1
        changed += 1

    print(f"Encrypted and cleared plaintext DOBs: {changed}")
    print("Verify plaintext count is zero before considering the backfill complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
