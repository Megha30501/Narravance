from flask import Blueprint, request, jsonify
from .models import db, Task, SalesData
from datetime import datetime
from .task_management import process_task 

api = Blueprint('routes', __name__)

@api.route('/', methods=['GET'])
def get_all_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'task_id': task.id,
        'name': task.name,
        'status': task.status,
        'created_at': task.created_at,
        'updated_at': task.updated_at
    } for task in tasks])


@api.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    
    task_name = data.get('name', 'New Task')
    filters = data.get('filters', {})
    new_task = Task(
        name=task_name,
        status='pending', 
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    process_task(new_task.id, filters)
    
    return jsonify({
        'task_id': new_task.id,
        'status': new_task.status
    }), 201


@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    
    task_data = []
    if task.status == 'completed':
        task_data = [{
            'company': sales.company,
            'car_model': sales.car_model,
            'date_of_sale': sales.date_of_sale,
            'price': sales.price
        } for sales in task.sales_data]  # Get associated sales data
    
    return jsonify({
        'task_id': task.id,
        'name': task.name,
        'status': task.status,
        'created_at': task.created_at,
        'updated_at': task.updated_at,
        'data': task_data  # Include data if task is completed
    })


@api.route('/analytics/<int:task_id>', methods=['GET'])
def get_task_analytics(task_id):
  
    task = Task.query.get_or_404(task_id)
    
    if task.status != 'completed':
        return jsonify({'error': 'Task is not completed yet.'}), 400
    
    sales_by_company = {}
    sales_by_model = {}
    sales_by_year = {}

    for record in task.sales_data:
        sales_by_company[record.company] = sales_by_company.get(record.company, 0) + record.price
        
        sales_by_model[record.car_model] = sales_by_model.get(record.car_model, 0) + record.price
        
        sale_year = record.date_of_sale.split('-')[0] 
        sales_by_year[sale_year] = sales_by_year.get(sale_year, 0) + record.price

    return jsonify({
        'sales_by_company': sales_by_company,
        'sales_by_model': sales_by_model,
        'sales_by_year': sales_by_year
    })

@api.route('/tasks/filter', methods=['GET'])
def filter_tasks():
    status = request.args.get('status')
    start_date = request.args.get('start_date')  
    end_date = request.args.get('end_date')  
    
    tasks_query = Task.query
    
    if status:
        tasks_query = tasks_query.filter(Task.status == status)
    
    if start_date:
        tasks_query = tasks_query.filter(Task.created_at >= datetime.fromisoformat(start_date))
    
    if end_date:
        tasks_query = tasks_query.filter(Task.created_at <= datetime.fromisoformat(end_date))
    
    tasks = tasks_query.all() 
    
    return jsonify([{
        'task_id': task.id,
        'name': task.name,
        'status': task.status,
        'created_at': task.created_at,
        'updated_at': task.updated_at
    } for task in tasks])