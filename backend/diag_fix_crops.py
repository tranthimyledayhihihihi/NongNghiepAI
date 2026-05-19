# -*- coding: utf-8 -*-
"""
Dedup CropTypes: delete garbled rows (and their dependent records),
keeping only the correct Unicode rows.
Strategy: correct-CropID rows already exist in PriceHistory/MarketPrices,
so we just DELETE garbled-CropID rows entirely.
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    all_crops = conn.execute(text(
        "SELECT CropID, CropName FROM CropTypes ORDER BY CropID"
    )).fetchall()

    garbled = [(cid, name) for cid, name in all_crops if '?' in (name or '')]
    correct_by_search = {}

    print("=== Garbled crops and their duplicates ===")
    for gcid, gname in garbled:
        clean_prefix = gname.replace('?', '%').replace('\xd0', '%')
        matches = conn.execute(
            text("SELECT CropID, CropName FROM CropTypes WHERE CropName LIKE :p AND CropID != :cid"),
            {"p": clean_prefix, "cid": gcid}
        ).fetchall()
        if matches:
            print(f"  Garbled: CropID={gcid} {repr(gname)}")
            for mcid, mname in matches:
                print(f"    → Correct: CropID={mcid} {repr(mname)}")
            correct_by_search[gcid] = matches[0][0]

    # Also include garbled with no match (orphans) — just delete them
    orphans = [cid for cid, name in garbled if cid not in correct_by_search]
    print(f"\nFound {len(correct_by_search)} garbled crops with correct duplicates")
    print(f"Found {len(orphans)} garbled crops with NO match (orphans): {orphans}")

    if not correct_by_search and not orphans:
        print("Nothing to clean up.")
    else:
        all_garbled_ids = list(correct_by_search.keys()) + orphans
        for garbled_cid in all_garbled_ids:
            correct_cid = correct_by_search.get(garbled_cid, None)
            print(f"\nCleaning CropID={garbled_cid} (correct={correct_cid})")
            with engine.begin() as txn:
                r = txn.execute(
                    text("DELETE FROM PriceHistory WHERE CropID=:g"),
                    {"g": garbled_cid}
                )
                print(f"  PriceHistory deleted: {r.rowcount} rows")

                r = txn.execute(
                    text("DELETE FROM MarketPrices WHERE CropID=:g"),
                    {"g": garbled_cid}
                )
                print(f"  MarketPrices deleted: {r.rowcount} rows")

                r = txn.execute(
                    text("DELETE FROM CropTypes WHERE CropID=:g"),
                    {"g": garbled_cid}
                )
                print(f"  CropTypes deleted: {r.rowcount} rows")

    print("\nDone.")
