from flask import Blueprint, request, jsonify
from .models import db, Task, SalesData
from datetime import datetime
from .task_management import process_task 

api = Blueprint('routes', __name__)

@api.route('/tasks', methods=['GET'])
def get_all_tasks():
    try:
        tasks = Task.query.all()
        print(f"Found {len(tasks)} tasks.")
        return jsonify([{
            'task_id': task.id,
            'status': task.status,
            'companies': task.companies,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        } for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        start_year = data.get('start_year')
        end_year = data.get('end_year')
        companies = data.get('companies')
        
        if not isinstance(start_year, int) or not isinstance(end_year, int):
            return jsonify({'error': 'start_year and end_year must be integers'}), 400
        if start_year > end_year:
            return jsonify({'error': 'start_year must be less than or equal to end_year'}), 400
        if companies and not isinstance(companies, str):
            return jsonify({'error': 'companies must be a string'}), 400
        if companies:
            companies = companies.strip()
            if not all(c.isalpha() or c in [',', ' '] for c in companies):
                return jsonify({'error': 'companies must contain only letters, commas, and spaces'}), 400

        new_task = Task( start_year=start_year, end_year=end_year, companies=companies)
        db.session.add(new_task)
        db.session.commit()
        
        process_task(new_task.id)
        
        return jsonify({
            'task_id': new_task.id,
            'status': new_task.status
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        task_data = []
        if task.status == 'completed':
            task_data = [{
                'company': sales.company,
                'car_model': sales.car_model,
                'date_of_sale': sales.date_of_sale,
                'price': sales.price
            } for sales in task.sales_data]  
        
        return jsonify({
            'task_id': task.id,
            'status': task.status,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
            'data': task_data 
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/analytics/<int:task_id>', methods=['GET'])
def get_task_analytics(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        if task.status != 'completed':
            return jsonify({'error': 'Task is not completed yet.'}), 400
        
        sales_by_company = {}
        sales_by_model = {}
        sales_by_year = {}

        for record in task.sales_data:
            sales_by_company[record.company] = sales_by_company.get(record.company, 0) + record.price
            
            sales_by_model[record.car_model] = sales_by_model.get(record.car_model, 0) + record.price
            
            try:
                sale_date = datetime.strptime(record.date_of_sale, '%Y-%m-%d')  # Assuming date format is YYYY-MM-DD
                sale_year = sale_date.year
                sales_by_year[sale_year] = sales_by_year.get(sale_year, 0) + record.price
            except ValueError:
                return jsonify({'error': f"Invalid date format for sale record {record.record_id}"}), 400

        return jsonify({
            'sales_by_company': sales_by_company,
            'sales_by_model': sales_by_model,
            'sales_by_year': sales_by_year
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500