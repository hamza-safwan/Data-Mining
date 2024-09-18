import pandas as pd
from sqlalchemy import create_engine

# Define the database connection string and the output file_path
database_connection_string = 'postgresql://username:password@localhost:5432/mydatabase'
output_file_path = 'bi_report.csv'

# Connect to the data warehouse
engine = create_engine(database_connection_string)

# Query: Fetch the required data
query = """
SELECT 
    date,
    SUM(amount) AS total_sales,
    COUNT(*) AS transactions_count
FROM 
    fact_sales
GROUP BY 
    date
ORDER BY 
    date;
"""
df = pd.read_sql(query, engine)

# Save the report to a CSV file
df.to_csv(output_file_path, index=False)

print("BI report generated successfully.")
