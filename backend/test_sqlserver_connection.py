"""
Test SQL Server connection
Run this to verify connection to NongNghiepAI database
"""
import pyodbc
from sqlalchemy import create_engine, text
from app.core.config import settings

def test_pyodbc_connection():
    """Test direct pyodbc connection"""
    print("Testing pyodbc connection...")
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-7T57RI\\SQLEXPRESS02;"
            "DATABASE=NongNghiepAI;"
            "UID=sa;"
            "PWD=123;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print("✓ pyodbc connection successful!")
        print(f"SQL Server version: {row[0][:50]}...")
        
        # List tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        print(f"\n✓ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ pyodbc connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n" + "="*50)
    print("Testing SQLAlchemy connection...")
    try:
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()
            print("✓ SQLAlchemy connection successful!")
            print(f"SQL Server version: {version[0][:50]}...")
            
            # Test query
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """))
            tables = result.fetchall()
            print(f"\n✓ Found {len(tables)} tables via SQLAlchemy")
            
        return True
    except Exception as e:
        print(f"✗ SQLAlchemy connection failed: {e}")
        return False

def check_tables():
    """Check if all required tables exist"""
    print("\n" + "="*50)
    print("Checking required tables...")
    
    required_tables = [
        'Users',
        'CropTypes',
        'HarvestSchedule',
        'MarketPrices',
        'PriceHistory',
        'QualityRecords',
        'AlertSubscriptions'
    ]
    
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-7T57RI\\SQLEXPRESS02;"
            "DATABASE=NongNghiepAI;"
            "UID=sa;"
            "PWD=123;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{table}'
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ {table}: exists ({count} rows)")
            else:
                print(f"✗ {table}: NOT FOUND")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("SQL Server Connection Test")
    print("Database: NongNghiepAI")
    print("="*50)
    
    # Test connections
    pyodbc_ok = test_pyodbc_connection()
    sqlalchemy_ok = test_sqlalchemy_connection()
    tables_ok = check_tables()
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"pyodbc connection: {'✓ OK' if pyodbc_ok else '✗ FAILED'}")
    print(f"SQLAlchemy connection: {'✓ OK' if sqlalchemy_ok else '✗ FAILED'}")
    print(f"Tables check: {'✓ OK' if tables_ok else '✗ FAILED'}")
    
    if pyodbc_ok and sqlalchemy_ok and tables_ok:
        print("\n🎉 All tests passed! Ready to use SQL Server.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
