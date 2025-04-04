import threading
import time
import json
import csv
from datetime import datetime
import os

from .models import db, Task, SalesData

# Simulated Job Queue
job_queue = []

def process_task(task_id, filters):
    # Add task to job queue
    job_queue.append((task_id, filters))

    # Run in a separate thread
    thread = threading.Thread(target=handle_task, args=(task_id, filters))
    thread.start()

def handle_task(task_id, filters):
    # Simulated delay before starting
    time.sleep(3)

    task = Task.query.get(task_id)
    task.status = 'in_progress'
    task.updated_at = datetime.utcnow()
    db.session.commit()

    # Load and filter source A (JSON)
    source_a_data = load_json_data('data/source_a.json')
    filtered_a = [
        record for record in source_a_data
        if apply_filters(record, filters, 'A')
    ]

    # Load and filter source B (CSV)
    filtered_b = load_csv_data('data/source_b.csv', filters)

    # Simulate processing time
    time.sleep(4)

    # Merge and insert to DB
    for record in filtered_a:
        sale = SalesData(
            task_id=task_id,
            source='A',
            company=record['company'],
            car_model=record['car_model'],
            date_of_sale=record['date_of_sale'],
            price=int(record['price'])
        )
        db.session.add(sale)

    for record in filtered_b:
        sale = SalesData(
            task_id=task_id,
            source='B',
            company=record['company'],
            car_model=record['car_model'],
            date_of_sale=record['date_of_sale'],
            price=int(record['price'])
        )
        db.session.add(sale)

    task.status = 'completed'
    task.updated_at = datetime.utcnow()
    db.session.commit()

def load_json_data(file_path):
    # Ensure that the path is correct and accessible
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file at {file_path}: {e}")
        return []

def load_csv_data(file_path, filters):
    filtered_data = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if apply_filters(row, filters, 'B'):
                    filtered_data.append(row)
    except Exception as e:
        print(f"Error reading CSV file at {file_path}: {e}")
    return filtered_data

def apply_filters(record, filters, source):
    # Basic filtering based on 'date_of_sale' and 'company'
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    allowed_companies = filters.get('companies')  # List of allowed companies like ['Honda', 'Toyota']

    record_date = record.get('date_of_sale')
    record_company = record.get('company')

    # Date filtering
    if start_date and record_date < start_date:
        return False
    if end_date and record_date > end_date:
        return False

    # Company filtering (optional for source A, mandatory for B if provided)
    if allowed_companies and record_company not in allowed_companies:
        return False

    return True
