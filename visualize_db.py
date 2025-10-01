#!/usr/bin/env python3
"""
SQLite Database Visualizer

This script provides various ways to visualize SQLite database data.
Usage: python visualize_db.py <database_name>
"""

import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def list_tables(cursor):
    """List all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]


def show_table_info(cursor, table_name):
    """Show basic information about a table."""
    # Get row count
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    row_count = cursor.fetchone()[0]
    
    # Get column info
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    columns = cursor.fetchall()
    
    print(f"\nTable: {table_name}")
    print(f"Rows: {row_count:,}")
    print(f"Columns: {len(columns)}")
    print("\nColumn Details:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    return row_count, columns


def show_sample_data(cursor, table_name, limit=10):
    """Show sample data from a table."""
    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit}')
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\nSample data from {table_name} (first {limit} rows):")
    print("-" * 80)
    
    # Print header
    print(" | ".join(f"{col:15}" for col in columns[:5]))  # Show first 5 columns
    print("-" * 80)
    
    # Print rows
    for row in rows:
        print(" | ".join(f"{str(val)[:15]:15}" for val in row[:5]))


def create_visualizations(df, table_name):
    """Create various visualizations of the data."""
    print(f"\nCreating visualizations for {table_name}...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Data Analysis: {table_name}', fontsize=16)
    
    # 1. Data types distribution
    ax1 = axes[0, 0]
    dtype_counts = df.dtypes.value_counts()
    dtype_counts.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Data Types Distribution')
    ax1.set_xlabel('Data Type')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Missing values heatmap
    ax2 = axes[0, 1]
    if df.shape[1] <= 20:  # Only show if not too many columns
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_data.plot(kind='bar', ax=ax2, color='coral')
            ax2.set_title('Missing Values by Column')
            ax2.set_xlabel('Column')
            ax2.set_ylabel('Missing Count')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Missing Values Check')
    else:
        ax2.text(0.5, 0.5, 'Too many columns\nfor missing values plot', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Missing Values Check')
    
    # 3. Numeric columns distribution
    ax3 = axes[1, 0]
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        # Show distribution of first numeric column
        first_numeric = numeric_cols[0]
        df[first_numeric].hist(bins=30, ax=ax3, color='lightgreen', alpha=0.7)
        ax3.set_title(f'Distribution of {first_numeric}')
        ax3.set_xlabel(first_numeric)
        ax3.set_ylabel('Frequency')
    else:
        ax3.text(0.5, 0.5, 'No Numeric Columns', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Numeric Data Distribution')
    
    # 4. Categorical columns
    ax4 = axes[1, 1]
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        # Show value counts for first categorical column
        first_categorical = categorical_cols[0]
        value_counts = df[first_categorical].value_counts().head(10)
        value_counts.plot(kind='bar', ax=ax4, color='lightcoral')
        ax4.set_title(f'Top 10 Values in {first_categorical}')
        ax4.set_xlabel(first_categorical)
        ax4.set_ylabel('Count')
        ax4.tick_params(axis='x', rotation=45)
    else:
        ax4.text(0.5, 0.5, 'No Categorical Columns', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Categorical Data Distribution')
    
    plt.tight_layout()
    
    # Save the plot
    output_file = f"{table_name}_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Visualization saved as: {output_file}")
    
    # Show the plot
    plt.show()


def analyze_database(database_name):
    """Main function to analyze the database."""
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        print(f"Analyzing database: {database_name}")
        print("=" * 50)
        
        # List all tables
        tables = list_tables(cursor)
        print(f"Found {len(tables)} table(s): {', '.join(tables)}")
        
        # Analyze each table
        for table_name in tables:
            show_table_info(cursor, table_name)
            show_sample_data(cursor, table_name)
            
            # Load data into pandas for visualization
            try:
                df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
                create_visualizations(df, table_name)
            except Exception as e:
                print(f"Could not create visualizations for {table_name}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python visualize_db.py <database_name>")
        print("Example: python visualize_db.py data.db")
        sys.exit(1)
    
    database_name = sys.argv[1]
    
    if not Path(database_name).exists():
        print(f"Error: Database '{database_name}' not found.")
        sys.exit(1)
    
    analyze_database(database_name)


if __name__ == "__main__":
    main()
