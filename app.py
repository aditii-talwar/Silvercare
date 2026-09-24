from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import random
import string
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = 'silvercare-safe-travel-companion-secret'

# Ensure database is initialized
init_db()

def generate_booking_code():
    chars = string.ascii_uppercase + string.digits
    return 'SC-' + ''.join(random.choices(chars, k=5))

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

        conn = get_db_connection()
        # Find an available companion to auto-match
        companion = conn.execute('SELECT * FROM companions WHERE is_available = 1 ORDER BY rating DESC, trips_completed DESC LIMIT 1').fetchone()
        companion_id = companion['id'] if companion else None

        status = 'Companion Assigned' if companion_id else 'Pending'

        conn.execute('''
            INSERT INTO bookings (
                booking_code, booked_by, booker_name, booker_phone, elderly_name, elderly_phone,
                pickup_location, destination, destination_type, service_date, service_time,
                assistance_needed, notes, status, companion_id, payment_status, total_fare
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 450)
        ''', (
            booking_code, booked_by, booker_name, booker_phone, elderly_name, elderly_phone,
            pickup_location, destination, destination_type, service_date, service_time,
            assistance_needed, notes, status, companion_id
        ))
        conn.commit()
        conn.close()

        flash(f'Companion successfully booked! Your booking tracking ID is {booking_code}.', 'success')
        return redirect(url_for('track', booking_code=booking_code))

    # Pre-fill from query params if coming from AI Assistant
    prefill = {
        'destination': request.args.get('destination', ''),
        'destination_type': request.args.get('destination_type', ''),
        'assistance': request.args.get('assistance', '')
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

@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip().lower()

    if not message:
        return jsonify({'reply': "Hello! I am SilverBot, your travel assistance guide. How can I help you or your family member today?"})

    reply = ""
    action_url = None

    if 'railway' in message or 'train' in message or 'station' in message:
        reply = "Our verified companions assist elders at railway stations with coolie/luggage coordination, platform navigation, wheelchair handling, and finding their seat and coach. Would you like to book station assistance?"
        action_url = url_for('book', destination_type='Railway Station', assistance='Luggage Support, Wheelchair Assistance, Ticket Guidance')
    elif 'hospital' in message or 'doctor' in message or 'clinic' in message:
        reply = "We provide patient and caring companions for hospital checkups, queue standing, wheelchair support, and pharmacy guidance. Would you like to schedule a hospital companion?"
        action_url = url_for('book', destination_type='Hospital', assistance='Wheelchair Assistance, Walking Support')
    elif 'airport' in message or 'flight' in message:
        reply = "For airport travel, companions assist with terminal entry, luggage trolley handling, security check accompaniment, and boarding gate navigation. Click below to book airport assistance."
        action_url = url_for('book', destination_type='Airport', assistance='Luggage Support, Wheelchair Assistance')
    elif 'safety' in message or 'verify' in message or 'verified' in message or 'trust' in message:
        reply = "Every Silvercare companion undergoes a strict 3-step verification: Government identity verification, local police verification, and elderly empathy & emergency first-aid training. You can also view live GPS updates throughout the trip."
        action_url = url_for('companions_list')
    elif 'track' in message or 'status' in message or 'where' in message:
        reply = "You can track your journey live in real time using your unique booking code (e.g. SC-XXXXX). Families receive constant reassurance at every milestone."
        action_url = url_for('track')
    elif 'price' in message or 'cost' in message or 'fare' in message:
        reply = "Silvercare companion assistance starts from a transparent flat rate of ₹450 per journey (up to 3 hours). Payment can be made easily post-trip via UPI, card, or auto-pay."
        action_url = url_for('book')
    else:
        reply = "I'm here to help elderly citizens travel with dignity and independence. You can book a verified companion for railway stations, hospitals, airports, or daily errands with complete live tracking."
        action_url = url_for('book')

    return jsonify({
        'reply': reply,
        'action_url': action_url,
        'action_label': 'Book Companion' if action_url else None
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
