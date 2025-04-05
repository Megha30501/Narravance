from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending')
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    companies = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    sales_data = db.relationship('SalesData', backref='task', lazy=True)
   
    def __repr__(self):
        return f'<Task {self.id} - {self.status}>'


class SalesData(db.Model):
    __tablename__ = 'sales'
    record_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    car_model = db.Column(db.String(50), nullable=False)
    date_of_sale = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
 
    def __repr__(self):
        return f'<SalesData {self.car_model} - {self.date_of_sale}>'