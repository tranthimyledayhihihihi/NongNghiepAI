# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    for tbl in ('CropTypes', 'MarketPrices', 'PriceHistory'):
        print(f"\n=== {tbl} ===")
        for r in conn.execute(text(
            f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH "
            f"FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tbl}' "
            f"AND DATA_TYPE IN ('varchar','nvarchar','text','ntext') ORDER BY ORDINAL_POSITION"
        )).fetchall():
            print(f"  {r[0]}: {r[1]}({r[2]})")
