from database import engine, Base
from models.user import User
from models.project import Project
from models.sprint import Sprint
from models.task import Task
from models.comment import Comment
# from models.ai import AI # Not in models dir
# from models.search_bar import SearchBar # In models dir but likely no FK to Project that blocks drop. 
# actually best to import just modules if I don't know class names, but Base.metadata uses imported classes.
# Let's import what I saw in `ls`: ai.py, search_bar.py
# I'll check file content of ai.py and search_bar.py if needed, but likely they depend on User/Project too.
# For now, let's fix known ones.
# from models.comments import Comment # Import if exists, check file system first

from sqlalchemy import text

print("Dropping schema public CASCADE...")
try:
    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext;"))
        connection.commit()
    print("Schema dropped and recreated successfully.")
except Exception as e:
    print(f"Error dropping schema: {e}")

print("Creating all tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
