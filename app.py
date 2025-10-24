from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# --------- Configuration ----------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration - optional. If you want real emails set these env vars.
# ---------------- EMAIL CONFIGURATION ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sasikalathennarasu5@gmail.com'     # 👉 replace with your Gmail
app.config['MAIL_PASSWORD'] = 'pnpq mdbs qsdu hqzs'        # 👉 replace with your generated app password
app.config['MAIL_DEFAULT_SENDER'] = ('Student Admission Portal', 'your_email@gmail.com')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# --------- Models ----------
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    remark = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<Applicant {self.full_name} - {self.status}>'

# --------- Utilities ----------
def send_email(subject, recipients, body):
    """Send email. If mail server not configured, save to sent_emails/ as fallback."""
    try:
        if app.config.get('MAIL_SERVER'):
            msg = Message(subject=subject, recipients=[recipients], body=body)
            mail.send(msg)
            print(f"Email sent to {recipients}")
        else:
            # fallback: write email to file so the user can inspect it
            os.makedirs('sent_emails', exist_ok=True)
            filename = f"sent_emails/email_to_{recipients.replace('@','_')}_{int(datetime.utcnow().timestamp())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"To: {recipients}\nSubject: {subject}\n\n{body}")
            print(f"MAIL_SERVER not configured — email saved to {filename}")
    except Exception as e:
        print('Error sending email:', e)

def send_sms(phone, message):
    """Placeholder SMS function.
    For real SMS, integrate with Twilio or other provider.
    This function writes SMS to sent_sms/ and prints to console so you have a record.
    """
    try:
        os.makedirs('sent_sms', exist_ok=True)
        filename = f"sent_sms/sms_to_{phone}_{int(datetime.utcnow().timestamp())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"To: {phone}\nMessage:\n{message}")
        print(f"SMS (simulated) saved to {filename}")
    except Exception as e:
        print('Error writing SMS simulation:', e)

@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# --------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        dob = request.form.get('dob', '').strip()

        if not full_name or not email or not phone or not course:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('apply'))

        applicant = Applicant(full_name=full_name, email=email, phone=phone, course=course, dob=dob)
        db.session.add(applicant)
        db.session.commit()

        # notify applicant (email + sms simulated)
        subject = 'Application Received - Student Admission Portal'
        body = f"Dear {full_name},\n\nThank you for applying for {course}. Your application id is {applicant.id} and is currently under review.\n\nRegards,\nAdmissions Team"
        send_email(subject, email, body)
        send_sms(phone, f"Hi {full_name}, your application (id {applicant.id}) has been received.")

        flash('Application submitted successfully! Check your email (or sent_emails folder).', 'success')
        return redirect(url_for('home'))

    return render_template('apply.html')

# Simple admin login (for demo). In production use proper auth.
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # default credentials: admin / admin123
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    applicants = Applicant.query.order_by(Applicant.applied_at.desc()).all()
    return render_template('admin_panel.html', applicants=applicants)

@app.route('/admin/view/<int:applicant_id>', methods=['GET', 'POST'])
def admin_view(applicant_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    applicant = Applicant.query.get_or_404(applicant_id)
    if request.method == 'POST':
        action = request.form.get('action')
        remark = request.form.get('remark', '')
        applicant.remark = remark
        if action == 'approve':
            applicant.status = 'Approved'
            db.session.commit()
            # notify applicant
            send_email('Application Approved', applicant.email, f"Congratulations {applicant.full_name}, your application (id {applicant.id}) has been APPROVED.")
            send_sms(applicant.phone, f"Your application (id {applicant.id}) has been APPROVED.")
            flash('Applicant approved and notified.', 'success')
        elif action == 'reject':
            applicant.status = 'Rejected'
            db.session.commit()
            send_email('Application Rejected', applicant.email, f"Dear {applicant.full_name}, we regret to inform you that your application (id {applicant.id}) has been REJECTED.")
            send_sms(applicant.phone, f"Your application (id {applicant.id}) has been REJECTED.")
            flash('Applicant rejected and notified.', 'warning')
        else:
            db.session.commit()
            flash('No action taken.', 'info')
        return redirect(url_for('admin_panel'))
    return render_template('admin_view.html', applicant=applicant)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# --------- CLI helper to init DB ----------
@app.cli.command('init-db')
def init_db():
    """Initialize the database (run: flask init-db)."""
    db.create_all()
    print('Initialized the database.')

if __name__ == '__main__':
    # ensure DB exists
    with app.app_context():
        db.create_all()
    app.run(debug=True)
