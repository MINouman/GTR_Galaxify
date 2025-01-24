from sqlalchemy import create_engine, Table, MetaData, select, Column, Integer, String
from sqlalchemy.dialects.postgresql import insert
import pandas as pd

# Database connection settings
user = 'admin'
password = 'Aikittam1'
host = 'localhost'
port = '5432'
db_name = 'samsung_phones'
table_name = 'phone_specs'

# SQLAlchemy engine
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')

# Reflect existing table structure from the database into MetaData
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables[table_name]

# Path to your CSV file
file_path = 'data.csv'
data = pd.read_csv(file_path)

# Connect to the database
with engine.connect() as conn:
    for _, row in data.iterrows():
        stmt = insert(table).values(**row.to_dict())
        do_nothing_stmt = stmt.on_conflict_do_update(
            index_elements=['id'],  # primary key or a unique column name
            set_={c.name: c for c in stmt.excluded if c.name != 'id'}
        )
        conn.execute(do_nothing_stmt)

print("Database has been updated from the CSV file.")
