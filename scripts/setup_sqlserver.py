"""
Setup SQL Server database for AgriAI
Creates all tables and inserts seed data
"""
import pyodbc
import os
from pathlib import Path

def get_connection():
    """Get SQL Server connection"""
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=NongNghiepAI;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

def execute_sql_file(cursor, file_path):
    """Execute SQL file"""
    print(f"Executing: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        # Split by GO statements
        statements = sql.split('GO')
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        print(f"  ✓ Success")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def setup_database():
    """Setup complete database"""
    print("="*60)
    print("AgriAI - SQL Server Database Setup")
    print("="*60)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("\n✓ Connected to NongNghiepAI database")
        
        # Get project root
        project_root = Path(__file__).parent.parent
        data_dir = project_root / 'data'
        
        # 1. Create tables
        print("\n" + "="*60)
        print("Step 1: Creating Tables")
        print("="*60)
        
        tables_dir = data_dir / 'tables'
        table_files = [
            'Users.sql',           # First - no dependencies
            'CropTypes.sql',       # Second - no dependencies
            'MarketPrices.sql',    # Third - no dependencies
            'PriceHistory.sql',    # Fourth - no dependencies
            'HarvestSchedule.sql', # Fifth - depends on CropTypes
            'QualityRecords.sql',  # Sixth - depends on Users
            'AlertSubscriptions.sql' # Seventh - depends on Users
        ]
        
        for table_file in table_files:
            file_path = tables_dir / table_file
            if file_path.exists():
                execute_sql_file(cursor, file_path)
                conn.commit()
            else:
                print(f"  ⚠ File not found: {table_file}")
        
        # 2. Insert seed data
        print("\n" + "="*60)
        print("Step 2: Inserting Seed Data")
        print("="*60)
        
        seeds_dir = data_dir / 'seeds'
        seed_files = [
            'seed_crop_types.sql',
            'seed_regions.sql',
            'seed_market_prices.sql'
        ]
        
        for seed_file in seed_files:
            file_path = seeds_dir / seed_file
            if file_path.exists():
                execute_sql_file(cursor, file_path)
                conn.commit()
            else:
                print(f"  ⚠ File not found: {seed_file}")
        
        # 3. Create stored procedures
        print("\n" + "="*60)
        print("Step 3: Creating Stored Procedures")
        print("="*60)
        
        sp_dir = data_dir / 'stored_procedures'
        sp_files = [
            'sp_GetHarvestForecast.sql',
            'sp_GetPriceHistory.sql',
            'sp_UpdateMarketPrice.sql'
        ]
        
        for sp_file in sp_files:
            file_path = sp_dir / sp_file
            if file_path.exists():
                execute_sql_file(cursor, file_path)
                conn.commit()
            else:
                print(f"  ⚠ File not found: {sp_file}")
        
        # 4. Verify setup
        print("\n" + "="*60)
        print("Step 4: Verifying Setup")
        print("="*60)
        
        cursor.execute("""
            SELECT TABLE_NAME, 
                   (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = t.TABLE_NAME) as column_count
            FROM INFORMATION_SCHEMA.TABLES t
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        print(f"\n✓ Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            row_count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {table[1]} columns, {row_count} rows")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Database setup completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python backend/test_sqlserver_connection.py")
        print("2. Start backend: cd backend && uvicorn app.main:app --reload")
        print("3. Access API docs: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()
