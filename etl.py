import pandas as pd
from sqlalchemy import create_engine

# Define the path to the CSV file and the database connection string
csv_file_path = 'source_data.csv'
database_connection_string = 'postgresql://username:password@localhost:5432/mydatabase'

# Extract: Load data from CSV
df = pd.read_csv(csv_file_path)

# Transform: Perform data cleaning and transformation
df['date'] = pd.to_datetime(df['date'])
df['amount'] = df['amount'].fillna(0)
df['amount'] = df['amount'].astype(float)

# Load: Insert data into the data warehouse
engine = create_engine(database_connection_string)
df.to_sql('fact_sales', engine, if_exists='replace', index=False)

print("ETL process completed successfully.")
