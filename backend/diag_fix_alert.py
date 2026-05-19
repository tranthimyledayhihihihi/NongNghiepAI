import sys
sys.path.insert(0, '.')
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    # Get check constraints on AlertSubscriptions
    sql = "SELECT cc.name, cc.definition FROM sys.check_constraints cc WHERE cc.parent_object_id = OBJECT_ID('AlertSubscriptions')"
    result = conn.execute(text(sql)).fetchall()
    print("CHECK constraints on AlertSubscriptions:")
    for r in result:
        print(" ", r[0], "->", r[1])

    # Get column data type
    sql2 = "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='AlertSubscriptions' AND COLUMN_NAME='AlertType'"
    result2 = conn.execute(text(sql2)).fetchall()
    print("AlertType column info:")
    for r in result2:
        print(" ", r)

    # Try to drop old constraint and add new one that allows accented values
    try:
        conn.execute(text("ALTER TABLE AlertSubscriptions DROP CONSTRAINT CK__AlertSubs__Alert__17236851"))
        conn.commit()
        print("Dropped old constraint")
    except Exception as e:
        print("Could not drop constraint:", e)
        conn.rollback()

    try:
        conn.execute(text("""
            ALTER TABLE AlertSubscriptions ADD CONSTRAINT CK_AlertSubs_AlertType
            CHECK (AlertType IN ('Tren', 'Duoi', 'Thay doi', N'Trên', N'Dưới', N'Thay đổi'))
        """))
        conn.commit()
        print("Added new constraint with Unicode support")
    except Exception as e:
        print("Could not add new constraint:", e)
        conn.rollback()
