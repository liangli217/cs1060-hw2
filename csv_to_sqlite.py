#!/usr/bin/env python3
"""
CSV to SQLite Converter

This script converts CSV files to SQLite databases.
Usage: python csv_to_sqlite.py <database_name> <csv_file_name>
"""

import sys
import csv
import sqlite3
import os
from pathlib import Path


def create_table_from_csv(cursor, csv_file, table_name):
    """
    Create a SQLite table from a CSV file.
    Automatically detects column types and creates appropriate schema.
    """
    with open(csv_file, 'r', encoding='utf-8-sig') as file:  # utf-8-sig handles BOM
        # Read the first few rows to determine column types
        sample_rows = []
        csv_reader = csv.reader(file)
        
        # Get header
        header = next(csv_reader)
        
        # Read sample rows for type detection
        for i, row in enumerate(csv_reader):
            if i >= 100:  # Sample first 100 rows for type detection
                break
            sample_rows.append(row)
        
        # Reset file pointer
        file.seek(0)
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header again
    
    # Determine column types
    column_types = []
    for i, col_name in enumerate(header):
        # Clean column name for SQLite (remove special characters, spaces)
        clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in col_name)
        # Check if original column name starts with a digit, not the cleaned name
        if col_name and col_name[0].isdigit():
            clean_name = 'col_' + clean_name
        
        # Check if column contains only numbers
        is_numeric = True
        is_integer = True
        
        for row in sample_rows:
            if i < len(row) and row[i].strip():
                value = row[i].strip()
                try:
                    # Try to convert to float first
                    float_val = float(value)
                    # Check if it's an integer
                    if not value.isdigit() and '.' in value:
                        is_integer = False
                except ValueError:
                    is_numeric = False
                    is_integer = False
                    break
        
        # Use TEXT for all columns (as requested)
        sql_type = 'TEXT'
        
        column_types.append((clean_name, sql_type))
    
    # Create table
    columns_sql = ', '.join([f'"{name}" {type_}' for name, type_ in column_types])
    create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})'
    
    cursor.execute(create_table_sql)
    
    return [col[0] for col in column_types]  # Return clean column names


def import_csv_data(cursor, csv_file, table_name, column_names):
    """
    Import CSV data into the SQLite table.
    """
    with open(csv_file, 'r', encoding='utf-8-sig') as file:  # utf-8-sig handles BOM
        csv_reader = csv.DictReader(file)
        
        # Prepare insert statement
        placeholders = ', '.join(['?' for _ in column_names])
        column_list = ', '.join([f'"{col}"' for col in column_names])
        insert_sql = f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})'
        
        # Import data in batches
        batch_size = 1000
        batch = []
        
        for row in csv_reader:
            # Convert row to list in the correct order
            values = []
            for col_name in column_names:
                # Find the original column name in the CSV
                original_col = None
                for orig_col in row.keys():
                    clean_orig = ''.join(c if c.isalnum() or c == '_' else '_' for c in orig_col)
                    if clean_orig[0].isdigit():
                        clean_orig = 'col_' + clean_orig
                    if clean_orig == col_name:
                        original_col = orig_col
                        break
                
                if original_col and original_col in row:
                    value = row[original_col]
                    # Convert empty strings to None for better SQLite handling
                    if value.strip() == '':
                        value = None
                    values.append(value)
                else:
                    values.append(None)
            
            batch.append(values)
            
            if len(batch) >= batch_size:
                cursor.executemany(insert_sql, batch)
                batch = []
        
        # Insert remaining rows
        if batch:
            cursor.executemany(insert_sql, batch)


def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_to_sqlite.py <database_name> <csv_file_name>")
        print("Example: python csv_to_sqlite.py health_data.db county_health_rankings.csv")
        sys.exit(1)
    
    database_name = sys.argv[1]
    csv_file_name = sys.argv[2]
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_name):
        print(f"Error: CSV file '{csv_file_name}' not found.")
        sys.exit(1)
    
    # Get table name from CSV filename (without extension)
    table_name = Path(csv_file_name).stem
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        print(f"Converting '{csv_file_name}' to SQLite database '{database_name}'...")
        print(f"Table name: '{table_name}'")
        
        # Create table and get column names
        column_names = create_table_from_csv(cursor, csv_file_name, table_name)
        print(f"Created table with {len(column_names)} columns")
        
        # Import data
        print("Importing data...")
        import_csv_data(cursor, csv_file_name, table_name, column_names)
        
        # Commit changes
        conn.commit()
        
        # Get row count
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        row_count = cursor.fetchone()[0]
        
        print(f"Successfully imported {row_count} rows into table '{table_name}'")
        
        # Show table schema
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns_info = cursor.fetchall()
        
        print("\nTable schema:")
        for col in columns_info:
            print(f"  {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
