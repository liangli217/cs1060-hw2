#!/usr/bin/env python3
"""
Simple SQLite Database Viewer

A lightweight tool to explore SQLite databases without external dependencies.
Usage: python simple_db_viewer.py <database_name>
"""

import sys
import sqlite3
from pathlib import Path


def list_tables(cursor):
    """List all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]


def show_table_schema(cursor, table_name):
    """Show the schema of a table."""
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    columns = cursor.fetchall()
    
    print(f"\nSchema for table '{table_name}':")
    print("-" * 60)
    print(f"{'Column Name':<25} {'Type':<15} {'Nullable':<10}")
    print("-" * 60)
    
    for col in columns:
        cid, name, data_type, not_null, default_val, pk = col
        nullable = "No" if not_null else "Yes"
        print(f"{name:<25} {data_type:<15} {nullable:<10}")


def show_sample_data(cursor, table_name, limit=20):
    """Show sample data from a table."""
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    total_rows = cursor.fetchone()[0]
    
    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit}')
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\nSample data from '{table_name}' (showing {min(limit, len(rows))} of {total_rows:,} rows):")
    print("=" * 100)
    
    # Print header
    header = " | ".join(f"{col[:12]:12}" for col in columns[:8])  # Show first 8 columns
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(f"{str(val)[:12]:12}" for val in row[:8])
        print(row_str)
    
    if total_rows > limit:
        print(f"... and {total_rows - limit:,} more rows")


def show_table_stats(cursor, table_name):
    """Show basic statistics for a table."""
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    row_count = cursor.fetchone()[0]
    
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    columns = cursor.fetchall()
    
    print(f"\nStatistics for '{table_name}':")
    print(f"  Total rows: {row_count:,}")
    print(f"  Total columns: {len(columns)}")
    
    # Show column statistics
    print("\nColumn details:")
    for col in columns:
        cid, name, data_type, not_null, default_val, pk = col
        print(f"  {name}: {data_type}")


def interactive_mode(cursor):
    """Interactive mode for running custom queries."""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("Enter SQL queries (type 'quit' to exit)")
    print("="*60)
    
    while True:
        try:
            query = input("\nsqlite> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.upper().startswith('SELECT'):
                results = cursor.fetchall()
                
                if results:
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    
                    # Print header
                    header = " | ".join(f"{col[:15]:15}" for col in column_names)
                    print(header)
                    print("-" * len(header))
                    
                    # Print results (limit to 50 rows for display)
                    for row in results[:50]:
                        row_str = " | ".join(f"{str(val)[:15]:15}" for val in row)
                        print(row_str)
                    
                    if len(results) > 50:
                        print(f"... and {len(results) - 50} more rows")
                else:
                    print("No results found.")
            else:
                print("Query executed successfully.")
                
        except Exception as e:
            print(f"Error: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_db_viewer.py <database_name>")
        print("Example: python simple_db_viewer.py data.db")
        sys.exit(1)
    
    database_name = sys.argv[1]
    
    if not Path(database_name).exists():
        print(f"Error: Database '{database_name}' not found.")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        print(f"SQLite Database Viewer")
        print(f"Database: {database_name}")
        print("=" * 50)
        
        # List all tables
        tables = list_tables(cursor)
        print(f"Tables found: {', '.join(tables)}")
        
        # Show information for each table
        for table_name in tables:
            show_table_stats(cursor, table_name)
            show_table_schema(cursor, table_name)
            show_sample_data(cursor, table_name)
        
        # Ask if user wants interactive mode
        print("\n" + "="*60)
        response = input("Enter interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_mode(cursor)
        
        conn.close()
        print("\nDatabase connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
