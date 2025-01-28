from flask import render_template, redirect, url_for, request, flash, current_app
from .models import Application
from werkzeug.utils import secure_filename
from . import db
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@current_app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        academic_background = request.form['academic_background']
        degree_certificate = request.files['degree_certificate']
        id_proof = request.files['id_proof']

        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        degree_certificate_filename = secure_filename(degree_certificate.filename)
        id_proof_filename = secure_filename(id_proof.filename)

        degree_certificate_path = os.path.join(upload_dir, degree_certificate_filename)
        id_proof_path = os.path.join(upload_dir, id_proof_filename)

        degree_certificate.save(degree_certificate_path)
        id_proof.save(id_proof_path)

        application = Application(
            name=name,
            email=email,
            academic_background=academic_background,
            degree_certificate=degree_certificate_filename,
            id_proof=id_proof_filename
        )
        db.session.add(application)
        db.session.commit()

        return redirect(url_for('success'))
    return render_template('apply.html')

@current_app.route('/success')
def success():
    return render_template('success.html')

@current_app.route('/admin/review')
def review():
    applications = Application.query.all()
    return render_template('review.html', applications=applications)

@current_app.route('/admin/approve/<int:application_id>')
def approve(application_id):
    application = Application.query.get(application_id)
    if application:
        application.status = 'Approved'
        db.session.commit()
        generate_admission_letter(application)
    return redirect(url_for('review'))

@current_app.route('/admin/reject/<int:application_id>')
def reject(application_id):
    application = Application.query.get(application_id)
    if application:
        application.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('review'))

def generate_admission_letter(application):
    letter_dir = os.path.join(current_app.static_folder, 'admission_letters')
    os.makedirs(letter_dir, exist_ok=True)

    file_path = os.path.join(letter_dir, f'{application.id}.pdf')
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, f"Admission Letter for {application.name}")
    c.drawString(100, 725, f"Email: {application.email}")
    c.drawString(100, 700, f"Academic Background: {application.academic_background}")
    c.save()
    return file_path
