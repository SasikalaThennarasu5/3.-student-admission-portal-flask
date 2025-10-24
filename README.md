# Student Admission Portal (Flask)
## Features
- Online registration form for students (apply page)
- Admin approval panel (admin login: admin / admin123)
- Email & SMS notification (simulated by default; configure MAIL_* env vars to send real emails)
- SQLite database (admissions.db)
- Bootstrap-based UI with responsive design

## Quick start
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   source venv/bin/activate   # macOS / Linux
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Configure email by setting environment variables:
   - MAIL_SERVER
   - MAIL_PORT
   - MAIL_USERNAME
   - MAIL_PASSWORD
   - MAIL_USE_TLS (True/False)
   - MAIL_USE_SSL (True/False)
   - MAIL_DEFAULT_SENDER
4. Initialize the database (optional, app will create it automatically):
   ```bash
   flask init-db
   ```
5. Run the app:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000/ in your browser.

## Admin dashboard
- URL: /admin
- Login: username `admin`, password `admin123`

## Notes
- If MAIL_SERVER is not configured, emails are saved to `sent_emails/` folder.
- SMS notifications are simulated and saved to `sent_sms/` folder. To send real SMS, integrate a provider like Twilio in `send_sms` function in `app.py`.
