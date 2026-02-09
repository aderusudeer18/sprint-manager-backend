from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result]
    print('Tables:', tables)
    
    # Check if user table exists and has CITEXT extension
    try:
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'citext'"))
        citext = result.fetchone()
        if citext:
            print("CITEXT extension is installed")
        else:
            print("WARNING: CITEXT extension is NOT installed!")
    except Exception as e:
        print(f"Error checking CITEXT: {e}")
