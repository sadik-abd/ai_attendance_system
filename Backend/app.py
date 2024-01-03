from flask import Flask
from flask import render_template,jsonify, request, redirect, url_for, session
from flask import Flask, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from constant import *
from records_db import Records
app = Flask(__name__)
app.secret_key = "kuttarBaccha"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_PATH
db = SQLAlchemy(app)
records_db = Records()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    image_path = db.Column(db.String(300))
    start_date = db.Column(db.Date)
    username = db.Column(db.String(120), unique=True, nullable=True)

@app.route('/', methods=["GET"])
def main():
    return render_template("index.html")

@app.route("/tables",methods=["GET"])
def tables():
    employees = Employee.query.all()
    print(employees)
    return render_template("tables.html",employees=employees)

def generate_username(name, id):
    formatted_name = name.replace(' ', '_').lower()
    return f"{formatted_name}{id}"

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    position = request.form.get('position', '')
    image = request.files['image']
    image_path = None

    new_employee = Employee(name=name, position=position, start_date=datetime.now().date())
    db.session.add(new_employee)
    db.session.commit()

    # Generate and update username
    new_employee.username = generate_username(new_employee.name, new_employee.id)
    
    if image:
        filename = secure_filename(new_employee.username)
        # Extract file extension and append to the username
        file_extension = os.path.splitext(image.filename)[1]
        filename_with_extension = f"{filename}{file_extension}"
        image_path = os.path.join(IMAGES_PATH, filename_with_extension)
        image.save(image_path)

        # Update the image path after saving the file
        new_employee.image_path = image_path
    records_db.add_user(new_employee.username,str(new_employee.start_date))
    db.session.commit()

    flash('Employee added successfully!', 'success')
    return redirect(url_for('register'))

@app.route('/register')
def register():
    return render_template('add_user.html')

@app.route('/delete')
def delete_employee():
    employee_id = request.args.get('user')
    employee = Employee.query.get(employee_id)
    if employee:
        os.remove(employee.image_path)
        db.session.delete(employee)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Employee not found"), 404

@app.route("/add_record",methods=["POST"])
def add_record():
    if request.is_json:
        # Get JSON data from the request
        data = request.get_json()


@app.route("/records")
def view_records():
    employee_id = request.args.get('user')
    employee = Employee.query.get(employee_id)
    data = records_db[employee.username]
    return render_template("records.html",data=data,len=len,max=max)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
