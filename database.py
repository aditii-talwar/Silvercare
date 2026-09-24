import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'silvercare.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Companions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            verified_badge INTEGER DEFAULT 1,
            rating REAL DEFAULT 4.9,
            trips_completed INTEGER DEFAULT 28,
            skills TEXT,
            photo_emoji TEXT DEFAULT '🧑‍💼',
            is_available INTEGER DEFAULT 1,
            bio TEXT
        )
    ''')

    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
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

    # Populate sample verified companions if table is empty
    cursor.execute('SELECT COUNT(*) FROM companions')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_companions = [
            (
                'Ramesh Sharma', '+91 98765 43210', 1, 4.9, 54,
                'Wheelchair Assistance, Railway Platform Navigation, Luggage Support, First Aid Certified',
                '👨‍💼', 1,
                'Background verified & police certified. Over 2 years of caring assistance for elders during railway travel.'
            ),
            (
                'Priya Deshmukh', '+91 98234 56789', 1, 5.0, 42,
                'Hospital Checkups, Airport Boarding, Medication Reminder, Wheelchair Assistance',
                '👩‍💼', 1,
                'Trained in patient care and mobility assistance. Calm, patient, and keeps family members constantly updated.'
            ),
            (
                'Arjun Nair', '+91 97456 12345', 1, 4.8, 36,
                'Bank & Government Office Paperwork, Bus Navigation, Heavy Luggage Handling',
                '🧑‍💼', 1,
                'Verified companion with extensive experience guiding elders through crowded stations and administrative visits.'
            ),
            (
                'Sunita Patel', '+91 98980 11223', 1, 4.9, 68,
                'Elder Companionship, Metro & Local Transit, Grocery/Temple Visits, Wheelchair Friendly',
                '👩‍💼', 1,
                'Warm and attentive companion with over 3 years of experience helping senior citizens travel independently.'
            )
        ]
        cursor.executemany('''
            INSERT INTO companions (name, phone, verified_badge, rating, trips_completed, skills, photo_emoji, is_available, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_companions)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
