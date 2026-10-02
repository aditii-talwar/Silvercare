import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'silvercare.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table (supports dual role: 'traveller' and 'companion')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'traveller',
            is_verified INTEGER DEFAULT 0,
            otp TEXT,
            otp_created_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Companions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            verified_badge INTEGER DEFAULT 1,
            rating REAL DEFAULT 4.9,
            trips_completed INTEGER DEFAULT 28,
            skills TEXT,
            photo_emoji TEXT DEFAULT '🧑‍💼',
            is_available INTEGER DEFAULT 1,
            bio TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            booked_by TEXT NOT NULL,
            booker_name TEXT NOT NULL,
            booker_phone TEXT NOT NULL,
            elderly_name TEXT NOT NULL,
            elderly_phone TEXT NOT NULL,
            pickup_location TEXT NOT NULL,
            destination TEXT NOT NULL,
            destination_type TEXT,
            service_date TEXT NOT NULL,
            service_time TEXT NOT NULL,
            assistance_needed TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Pending',
            companion_id INTEGER,
            payment_status TEXT DEFAULT 'Pending',
            total_fare INTEGER DEFAULT 450,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (companion_id) REFERENCES companions(id)
        )
    ''')

    # Reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            companion_id INTEGER,
            rating INTEGER NOT NULL,
            reviewer_name TEXT NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (companion_id) REFERENCES companions(id)
        )
    ''')

    # Populate seed users if empty
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        demo_hash = generate_password_hash('demo123')
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash, role, is_verified)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', ('Aditi (Traveller Demo)', 'traveller@demo.com', '+91 98765 00001', demo_hash, 'traveller'))
        
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash, role, is_verified)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', ('Ramesh Sharma (Companion Demo)', 'companion@demo.com', '+91 98765 43210', demo_hash, 'companion'))

    # Populate sample verified companions if table is empty
    cursor.execute('SELECT COUNT(*) FROM companions')
    count = cursor.fetchone()[0]
    if count == 0:
        # Find companion demo user id if present
        comp_user = cursor.execute('SELECT id FROM users WHERE email = ?', ('companion@demo.com',)).fetchone()
        comp_user_id = comp_user[0] if comp_user else None

        sample_companions = [
            (
                comp_user_id, 'Ramesh Sharma', '+91 98765 43210', 1, 4.9, 54,
                'Wheelchair Assistance, Railway Platform Navigation, Luggage Support, First Aid Certified',
                '👨‍💼', 1,
                'Background verified & police certified. Over 2 years of caring assistance for elders during railway travel.'
            ),
            (
                None, 'Priya Deshmukh', '+91 98234 56789', 1, 5.0, 42,
                'Hospital Checkups, Airport Boarding, Medication Reminder, Wheelchair Assistance',
                '👩‍💼', 1,
                'Trained in patient care and mobility assistance. Calm, patient, and keeps family members constantly updated.'
            ),
            (
                None, 'Arjun Nair', '+91 97456 12345', 1, 4.8, 36,
                'Bank & Government Office Paperwork, Bus Navigation, Heavy Luggage Handling',
                '🧑‍💼', 1,
                'Verified companion with extensive experience guiding elders through crowded stations and administrative visits.'
            ),
            (
                None, 'Sunita Patel', '+91 98980 11223', 1, 4.9, 68,
                'Elder Companionship, Metro & Local Transit, Grocery/Temple Visits, Wheelchair Friendly',
                '👩‍💼', 1,
                'Warm and attentive companion with over 3 years of experience helping senior citizens travel independently.'
            )
        ]
        cursor.executemany('''
            INSERT INTO companions (user_id, name, phone, verified_badge, rating, trips_completed, skills, photo_emoji, is_available, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_companions)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
