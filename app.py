from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import random
import string
import os
import json
import urllib.request
import urllib.error
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
from bhashini import process_bhashini_chat, SUPPORTED_LANGUAGES

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'silvercare-safe-travel-companion-secret')

# Google Apps Script Web App URL (Relays emails over HTTPS Port 443)
GAS_WEBAPP_URL = os.environ.get('GAS_WEBAPP_URL', '')

# Ensure database is initialized
init_db()

def generate_booking_code():
    chars = string.ascii_uppercase + string.digits
    return 'SC-' + ''.join(random.choices(chars, k=5))

def send_otp_email(to_email, otp, user_name="Traveller"):
    """
    Sends OTP email:
    - If demo/test email: Flags as demo mode so OTP is displayed on screen.
    - If real email & GAS_WEBAPP_URL configured: Dispatches via Google Apps Script (Port 443).
    - If real email & no GAS_WEBAPP_URL: Falls back to demo display for seamless testing.
    """
    to_email_lower = to_email.lower().strip()
    is_demo = ('demo' in to_email_lower or 'test' in to_email_lower or to_email_lower.endswith('@demo.com'))

    if is_demo or not GAS_WEBAPP_URL:
        # Demo mode: Display OTP directly on screen
        reason = "Demo Email Detected" if is_demo else "Google Apps Script Relay URL Not Set (Demo Mode)"
        return {
            'success': False,
            'is_demo': True,
            'reason': reason,
            'otp': otp,
            'message': f"[{reason}] Your verification code is: {otp}"
        }

    # Dispatch via Google Apps Script over HTTPS Port 443
    try:
        payload = json.dumps({
            "to": to_email,
            "otp": otp,
            "name": user_name,
            "subject": "Your Silvercare Travel Verification Code"
        }).encode('utf-8')

        req = urllib.request.Request(
            GAS_WEBAPP_URL,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get('status') == 'success':
                return {
                    'success': True,
                    'is_demo': False,
                    'message': f"A 6-digit verification code was sent to {to_email} via Google Apps Script (Port 443)."
                }
            else:
                return {
                    'success': False,
                    'is_demo': True,
                    'otp': otp,
                    'message': f"Email service notice: {res_data.get('message', 'Failed to dispatch')}. Demo OTP: {otp}"
                }
    except Exception as e:
        print(f"Error dispatching email via Google Apps Script (Port 443): {e}")
        return {
            'success': False,
            'is_demo': True,
            'otp': otp,
            'message': f"Could not reach Google Apps Script (Port 443). Demo OTP displayed: {otp}"
        }

@app.context_processor
def inject_global_context():
    """Provides user session and language options to all templates."""
    current_user = None
    if 'user_id' in session:
        current_user = {
            'id': session['user_id'],
            'name': session.get('user_name', 'User'),
            'role': session.get('role', 'traveller'),
            'email': session.get('user_email', '')
        }
    return {
        'current_user': current_user,
        'supported_languages': SUPPORTED_LANGUAGES,
        'current_language': session.get('selected_language', 'en')
    }

# ================= AUTHENTICATION & OTP ROUTES =================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'traveller').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not (name and email and password):
            flash('Please provide your name, email, and password.', 'danger')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('signup.html')

        if role not in ['traveller', 'companion']:
            role = 'traveller'

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user and existing_user['is_verified'] == 1:
            conn.close()
            flash('An account with this email already exists. Please log in.', 'info')
            return redirect(url_for('login', role=role))

        # Generate 6-digit numeric OTP
        otp = str(random.randint(100000, 999999))
        password_hash = generate_password_hash(password)

        if existing_user:
            # Update unverified user
            conn.execute('''
                UPDATE users SET name = ?, phone = ?, password_hash = ?, role = ?, otp = ?, otp_created_at = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (name, phone, password_hash, role, otp, email))
        else:
            conn.execute('''
                INSERT INTO users (name, email, phone, password_hash, role, is_verified, otp, otp_created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?, CURRENT_TIMESTAMP)
            ''', (name, email, phone, password_hash, role, otp))

        conn.commit()
        conn.close()

        # Send OTP (Real email via GAS over port 443, or Demo fallback)
        email_result = send_otp_email(email, otp, name)

        session['pending_email'] = email
        session['pending_role'] = role
        if email_result.get('is_demo'):
            session['demo_otp'] = otp
        else:
            session.pop('demo_otp', None)

        flash(email_result['message'], 'info' if email_result.get('is_demo') else 'success')
        return redirect(url_for('verify_otp'))

    role_param = request.args.get('role', 'traveller')
    return render_template('signup.html', selected_role=role_param)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    pending_email = session.get('pending_email')
    if not pending_email:
        flash('No registration pending. Please sign up or log in.', 'warning')
        return redirect(url_for('signup'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (pending_email,)).fetchone()

        if user and user['otp'] and user['otp'] == entered_otp:
            # Mark user verified
            conn.execute('UPDATE users SET is_verified = 1, otp = NULL WHERE id = ?', (user['id'],))
            
            # If companion, ensure a profile row exists in companions table
            if user['role'] == 'companion':
                comp_profile = conn.execute('SELECT * FROM companions WHERE user_id = ?', (user['id'],)).fetchone()
                if not comp_profile:
                    conn.execute('''
                        INSERT INTO companions (user_id, name, phone, verified_badge, rating, trips_completed, skills, bio)
                        VALUES (?, ?, ?, 1, 5.0, 0, 'Mobility Assistance, Luggage Handling', 'Newly verified caring companion ready to assist.')
                    ''', (user['id'], user['name'], user['phone'] or ''))
            
            conn.commit()
            conn.close()

            # Log user in
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session['user_email'] = user['email']

            session.pop('pending_email', None)
            session.pop('demo_otp', None)

            flash(f'Welcome, {user["name"]}! Your account is verified and ready.', 'success')
            if user['role'] == 'companion':
                return redirect(url_for('companion_portal'))
            return redirect(url_for('index'))
        else:
            conn.close()
            flash('Invalid OTP code. Please check and enter the correct 6-digit code.', 'danger')

    demo_otp = session.get('demo_otp')
    return render_template('verify_otp.html', email=pending_email, demo_otp=demo_otp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    selected_role = request.args.get('role', 'traveller').lower()
    if selected_role not in ['traveller', 'companion']:
        selected_role = 'traveller'

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'traveller').strip().lower()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if not user:
            flash('No account found with this email. Please sign up first.', 'danger')
            return render_template('login.html', selected_role=role)

        if user['role'] != role:
            flash(f'This account is registered as a {user["role"].capitalize()}. Please switch tabs to log in.', 'warning')
            return render_template('login.html', selected_role=role)

        if not check_password_hash(user['password_hash'], password):
            flash('Incorrect password. Please try again.', 'danger')
            return render_template('login.html', selected_role=role)

        if user['is_verified'] == 0:
            # Resend OTP
            otp = str(random.randint(100000, 999999))
            conn = get_db_connection()
            conn.execute('UPDATE users SET otp = ?, otp_created_at = CURRENT_TIMESTAMP WHERE id = ?', (otp, user['id']))
            conn.commit()
            conn.close()

            email_result = send_otp_email(user['email'], otp, user['name'])
            session['pending_email'] = user['email']
            session['pending_role'] = user['role']
            if email_result.get('is_demo'):
                session['demo_otp'] = otp

            flash('Please verify your account with the OTP before logging in.', 'info')
            return redirect(url_for('verify_otp'))

        # Successful Login
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']
        session['user_email'] = user['email']

        flash(f'Welcome back, {user["name"]}!', 'success')
        if user['role'] == 'companion':
            return redirect(url_for('companion_portal'))
        return redirect(url_for('index'))

    return render_template('login.html', selected_role=selected_role)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# ================= CORE APPLICATION ROUTES =================

@app.route('/')
def index():
    conn = get_db_connection()
    companions = conn.execute('SELECT * FROM companions WHERE is_available = 1 LIMIT 3').fetchall()
    total_completed = conn.execute('SELECT SUM(trips_completed) FROM companions').fetchone()[0] or 180
    conn.close()
    return render_template('index.html', companions=companions, total_completed=total_completed)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        booked_by = request.form.get('booked_by', 'Elderly Citizen')
        booker_name = request.form.get('booker_name', '').strip()
        booker_phone = request.form.get('booker_phone', '').strip()
        elderly_name = request.form.get('elderly_name', '').strip()
        elderly_phone = request.form.get('elderly_phone', '').strip()
        pickup_location = request.form.get('pickup_location', '').strip()
        destination = request.form.get('destination', '').strip()
        destination_type = request.form.get('destination_type', 'Other')
        service_date = request.form.get('service_date', '').strip()
        service_time = request.form.get('service_time', '').strip()
        notes = request.form.get('notes', '').strip()

        # Collect assistance checkboxes
        assistance_list = request.form.getlist('assistance')
        assistance_needed = ', '.join(assistance_list) if assistance_list else 'General Companionship'

        if not (booker_name and pickup_location and destination and service_date and service_time):
            flash('Please fill in all essential details to schedule your companion.', 'danger')
            return redirect(url_for('book'))

        if not elderly_name:
            elderly_name = booker_name
        if not elderly_phone:
            elderly_phone = booker_phone

        booking_code = generate_booking_code()
        user_id = session.get('user_id')

        conn = get_db_connection()
        # Find an available companion to auto-match
        companion = conn.execute('SELECT * FROM companions WHERE is_available = 1 ORDER BY rating DESC, trips_completed DESC LIMIT 1').fetchone()
        companion_id = companion['id'] if companion else None

        status = 'Companion Assigned' if companion_id else 'Pending'

        conn.execute('''
            INSERT INTO bookings (
                booking_code, user_id, booked_by, booker_name, booker_phone, elderly_name, elderly_phone,
                pickup_location, destination, destination_type, service_date, service_time,
                assistance_needed, notes, status, companion_id, payment_status, total_fare
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 450)
        ''', (
            booking_code, user_id, booked_by, booker_name, booker_phone, elderly_name, elderly_phone,
            pickup_location, destination, destination_type, service_date, service_time,
            assistance_needed, notes, status, companion_id
        ))
        conn.commit()
        conn.close()

        flash(f'Companion successfully booked! Your booking tracking ID is {booking_code}.', 'success')
        return redirect(url_for('track', booking_code=booking_code))

    # Pre-fill from query params or logged-in user
    prefill = {
        'destination': request.args.get('destination', ''),
        'destination_type': request.args.get('destination_type', ''),
        'assistance': request.args.get('assistance', ''),
        'booker_name': session.get('user_name', '') if session.get('user_name') else ''
    }
    return render_template('book.html', prefill=prefill)

@app.route('/track')
@app.route('/track/<booking_code>')
def track(booking_code=None):
    if not booking_code:
        booking_code = request.args.get('booking_code', '').strip().upper()
        if not booking_code:
            return render_template('track_search.html')
        return redirect(url_for('track', booking_code=booking_code))

    conn = get_db_connection()
    booking = conn.execute('''
        SELECT b.*, c.name AS companion_name, c.phone AS companion_phone, 
               c.rating AS companion_rating, c.trips_completed, c.photo_emoji, c.skills
        FROM bookings b
        LEFT JOIN companions c ON b.companion_id = c.id
        WHERE b.booking_code = ?
    ''', (booking_code,)).fetchone()
    conn.close()

    if not booking:
        flash(f'Booking with code "{booking_code}" not found. Please check and try again.', 'warning')
        return render_template('track_search.html')

    return render_template('tracking.html', booking=booking)

@app.route('/api/booking-status/<booking_code>')
def booking_status_api(booking_code):
    conn = get_db_connection()
    booking = conn.execute('''
        SELECT b.status, b.payment_status, c.name AS companion_name, c.phone AS companion_phone
        FROM bookings b
        LEFT JOIN companions c ON b.companion_id = c.id
        WHERE b.booking_code = ?
    ''', (booking_code,)).fetchone()
    conn.close()

    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    return jsonify({
        'status': booking['status'],
        'payment_status': booking['payment_status'],
        'companion_name': booking['companion_name'],
        'companion_phone': booking['companion_phone']
    })

@app.route('/companions')
def companions_list():
    conn = get_db_connection()
    companions = conn.execute('SELECT * FROM companions ORDER BY rating DESC').fetchall()
    conn.close()
    return render_template('companions_list.html', companions=companions)

@app.route('/companion-portal')
def companion_portal():
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.*, c.name AS companion_name
        FROM bookings b
        LEFT JOIN companions c ON b.companion_id = c.id
        ORDER BY b.id DESC
    ''').fetchall()
    conn.close()
    return render_template('companion_portal.html', bookings=bookings)

@app.route('/companion/update-status/<int:booking_id>/<new_status>', methods=['POST'])
def update_status(booking_id, new_status):
    valid_statuses = ['Companion Assigned', 'Arrived at Pickup', 'In Transit', 'Completed', 'Cancelled']
    if new_status in valid_statuses:
        conn = get_db_connection()
        conn.execute('UPDATE bookings SET status = ? WHERE id = ?', (new_status, booking_id))
        conn.commit()
        conn.close()
        flash(f'Booking #{booking_id} status updated to: {new_status}', 'info')
    return redirect(url_for('companion_portal'))

@app.route('/pay/<booking_code>', methods=['GET', 'POST'])
def pay(booking_code):
    conn = get_db_connection()
    booking = conn.execute('SELECT * FROM bookings WHERE booking_code = ?', (booking_code,)).fetchone()

    if not booking:
        conn.close()
        flash('Booking not found', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        method = request.form.get('payment_method', 'UPI / Auto-Pay')
        conn.execute('UPDATE bookings SET payment_status = "Paid" WHERE booking_code = ?', (booking_code,))
        conn.commit()
        conn.close()
        flash(f'Payment of ₹{booking["total_fare"]} received successfully via {method}! Thank you.', 'success')
        return redirect(url_for('review', booking_code=booking_code))

    conn.close()
    return render_template('pay.html', booking=booking)

@app.route('/review/<booking_code>', methods=['GET', 'POST'])
def review(booking_code):
    conn = get_db_connection()
    booking = conn.execute('''
        SELECT b.*, c.name AS companion_name 
        FROM bookings b 
        LEFT JOIN companions c ON b.companion_id = c.id 
        WHERE b.booking_code = ?
    ''', (booking_code,)).fetchone()

    if not booking:
        conn.close()
        flash('Booking not found', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        reviewer_name = request.form.get('reviewer_name', booking['elderly_name'])
        comment = request.form.get('comment', '').strip()

        conn.execute('''
            INSERT INTO reviews (booking_id, companion_id, rating, reviewer_name, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking['id'], booking['companion_id'], rating, reviewer_name, comment))
        conn.commit()
        conn.close()
        flash('Thank you for rating your companion! Your feedback reassures our entire community.', 'success')
        return redirect(url_for('index'))

    conn.close()
    return render_template('review.html', booking=booking)

# ================= BHASHINI MULTILINGUAL CHATBOT API =================

@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    language = (data.get('language') or session.get('selected_language') or 'en').strip()

    # Process using Bhashini AI engine
    result = process_bhashini_chat(message, language=language)

    action_url = None
    if result.get('action_type'):
        action_url = url_for('book', destination_type=result['action_type'], assistance=result.get('action_asst', ''))

    return jsonify({
        'reply': result['reply'],
        'language': result['language'],
        'language_name': result['language_name'],
        'action_url': action_url,
        'action_label': 'Book Companion' if action_url else None
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
