from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    date = db.Column(db.String(20))
    status = db.Column(db.String(10))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    today = datetime.date.today().strftime('%d-%m-%Y')
    students = Student.query.all()
    return render_template('dashboard.html', students=students, today=today)

@app.route('/mark', methods=['POST'])
def mark():
    date = datetime.date.today().strftime('%d-%m-%Y')
    for student in Student.query.all():
        status = request.form.get(str(student.id))
        record = Attendance(student_id=student.id, date=date, status=status)
        db.session.add(record)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/export')
def export_pdf():
    today = datetime.date.today().strftime('%d-%m-%Y')
    c = canvas.Canvas('absentees.pdf', pagesize=A4)
    y = 800
    c.setFont('Helvetica-Bold', 14)
    c.drawString(150, y, f'Absent Students Report - {today}')
    y -= 40

    records = Attendance.query.filter_by(date=today, status='Absent').all()
    c.setFont('Helvetica', 11)
    for r in records:
        student = Student.query.get(r.student_id)
        c.drawString(100, y, f"{student.reg_no} - {student.name}")
        y -= 20

    c.save()
    Attendance.query.filter_by(date=today).delete()
    db.session.commit()
    return send_file('absentees.pdf', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Student.query.count() == 0:
            db.session.add(Student(reg_no='SRM001', name='Arun Kumar'))
            db.session.add(Student(reg_no='SRM002', name='Priya Sharma'))
            db.session.add(Student(reg_no='SRM003', name='Rahul Singh'))
            db.session.commit()
    app.run()
