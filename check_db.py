from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

print("Tables in the database:")
print(inspector.get_table_names())