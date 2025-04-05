import time
import os
import json
import pandas as pd
import csv
from datetime import datetime
import logging
from contextlib import contextmanager
from queue import Queue
from threading import Thread


from .models import db, Task, SalesData

job_queue = []


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of database operations."""
    session = db.session() 
    try:
        yield session  
        session.commit() 
    except Exception:
        session.rollback()
        raise
    finally:
        session.close() 

def fetch_data_from_sources(start_year, end_year, companies):
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Read data from Source A (JSON)
    source_a_path = os.path.join(data_folder, 'sales_data.json')
    with open(source_a_path, 'r') as f:
        source_a_data = json.load(f)

    # Read data from Source B (CSV)
    source_b_path = os.path.join(data_folder, 'sales_data.csv')
    source_b_data = pd.read_csv(source_b_path)

    # Combine and filter the data
    combined_data = source_a_data + source_b_data.to_dict(orient='records')
    print("Combined Data:", combined_data)  # Debugging line to see what data is being combined

    # Filter the data based on the provided arguments
    filtered_data = []
    for record in combined_data:
        # Extract the year from the date_of_sale (first 4 characters are the year)
        year = int(record['date_of_sale'].split('-')[0])
        
        # Check if the year is within the specified range
        if start_year <= year <= end_year:
            # Check if the company is in the list of selected companies
            if any(company.strip() in record['company'] for company in companies.split(',')):
                filtered_data.append(record)

    print("Filtered Data:", filtered_data)  # Debugging line to check if filtering is correct

    return filtered_data


def process_task( task_id):
    task = Task.query.get(task_id)
    task.status = 'in progress'
    db.session.commit()
    
    # Simulate fetching data from external sources and processing it
    data = fetch_data_from_sources(task.start_year, task.end_year, task.companies)
    
    if not data:
        print(f"No data to process for task {task_id}.") 
    # Simulate another delay for processing
    time.sleep(5)
    
    # Store data into the database (SalesData model)
    for record in data:
        print(f"Adding record to SalesData: {record}")  
        sales_data = SalesData(
            task_id=task.id,
            company=record.get('company'),
            car_model=record.get('car_model'),
            date_of_sale=record.get('date_of_sale'),
            price=record.get('price')
        )
        db.session.add(sales_data)
    
    task.status = 'completed'
    db.session.commit()


def add_task_to_queue(task_id):
    job_queue.put(task_id)
    task_thread = Thread(target=process_task, args=(task_id,))
    task_thread.start()

