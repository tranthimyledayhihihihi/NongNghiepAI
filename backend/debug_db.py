import sys
sys.path.insert(0, '.')
import unicodedata
from app.core.database import SessionLocal
from app.models.crop import CropType
from sqlalchemy import text

db = SessionLocal()

# Check normalization form of values in Python source
for name in ["Lúa", "Sầu riêng", "Hồ tiêu"]:
    print(f"\n'{name}':")
    print(f"  NFC:  {[hex(ord(c)) for c in unicodedata.normalize('NFC', name)]}")
    print(f"  NFD:  {[hex(ord(c)) for c in unicodedata.normalize('NFD', name)]}")
    nfc_name = unicodedata.normalize("NFC", name)
    nfd_name = unicodedata.normalize("NFD", name)

    r1 = db.query(CropType).filter(CropType.CropName == nfc_name).first()
    r2 = db.query(CropType).filter(CropType.CropName == nfd_name).first()
    print(f"  == NFC => {repr(r1.CropName) if r1 else None}")
    print(f"  == NFD => {repr(r2.CropName) if r2 else None}")

# Check what comes back from DB
print("\nDB values codepoints:")
rows = db.execute(text("SELECT CropID, CropName FROM CropTypes WHERE CropID IN (1,4,10)")).fetchall()
for row in rows:
    name = row[1]
    print(f"  CropID={row[0]} '{name}': {[hex(ord(c)) for c in name]}")

db.close()
