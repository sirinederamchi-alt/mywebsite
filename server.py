from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import json
import os

app = Flask(__name__)
CORS(app)

# Database setup
DB_PATH = 'users.db'

def init_db():
    """Initialize the database with users table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT NOT NULL,
        lastName TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        skin_type TEXT,
        concerns TEXT,
        allergies TEXT,
        routine_level TEXT,
        notes TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute("PRAGMA table_info(quiz_results)")
    existing_cols = {row[1] for row in c.fetchall()}
    if "notes" not in existing_cols:
        c.execute("ALTER TABLE quiz_results ADD COLUMN notes TEXT")
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.json
        
        # Validate required fields
        if not all(k in data for k in ['firstName', 'lastName', 'email', 'password']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        firstName = data['firstName'].strip()
        lastName = data['lastName'].strip()
        email = data['email'].strip().lower()
        phone = data.get('phone', '').strip()
        password = data['password']
        
        # Validate inputs
        if not firstName or not lastName or not email or not password:
            return jsonify({'success': False, 'message': 'Empty fields are not allowed'}), 400
        
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO users (firstName, lastName, email, phone, password)
                        VALUES (?, ?, ?, ?, ?)''',
                     (firstName, lastName, email, phone, hashed_password))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'user': {
                    'firstName': firstName,
                    'lastName': lastName,
                    'email': email
                }
            }), 201
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered'}), 409
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        hashed_password = hash_password(password)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('SELECT id, firstName, lastName, email FROM users WHERE email = ? AND password = ?',
                 (email, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user[0],
                    'firstName': user[1],
                    'lastName': user[2],
                    'email': user[3]
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
def save_quiz():
    """Save latest quiz result for a user"""
    try:
        data = request.json or {}
        user_id = data.get('userId')
        if not user_id:
            return jsonify({'success': False, 'message': 'Missing userId'}), 400

        skin_type = data.get('skinType', '').strip()
        routine_level = data.get('routineLevel', '').strip()
        concerns = json.dumps(data.get('concerns', []))
        allergies = json.dumps(data.get('allergies', []))
        notes = data.get('notes', '').strip()
        recommendations = json.dumps(data.get('recommendations', []))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO quiz_results (user_id, skin_type, concerns, allergies, routine_level, notes, recommendations)
                     VALUES (?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT(user_id) DO UPDATE SET
                       skin_type=excluded.skin_type,
                       concerns=excluded.concerns,
                       allergies=excluded.allergies,
                       routine_level=excluded.routine_level,
                       notes=excluded.notes,
                       recommendations=excluded.recommendations,
                       created_at=CURRENT_TIMESTAMP
                  ''', (user_id, skin_type, concerns, allergies, routine_level, notes, recommendations))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Quiz saved'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def profile():
    """Get user profile and latest quiz result"""
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'success': False, 'message': 'Missing userId'}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, firstName, lastName, email FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404

        c.execute('''SELECT skin_type, concerns, allergies, routine_level, notes, recommendations, created_at
                     FROM quiz_results WHERE user_id = ?''', (user_id,))
        quiz = c.fetchone()
        conn.close()

        quiz_payload = None
        if quiz:
            quiz_payload = {
                'skinType': quiz[0],
                'concerns': json.loads(quiz[1] or '[]'),
                'allergies': json.loads(quiz[2] or '[]'),
                'routineLevel': quiz[3],
                'notes': quiz[4],
                'recommendations': json.loads(quiz[5] or '[]'),
                'createdAt': quiz[6]
            }

        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'firstName': user[1],
                'lastName': user[2],
                'email': user[3]
            },
            'quiz': quiz_payload
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users (for testing purposes)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, firstName, lastName, email, phone, created_at FROM users')
        users = c.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': [
                {
                    'id': u[0],
                    'firstName': u[1],
                    'lastName': u[2],
                    'email': u[3],
                    'phone': u[4],
                    'created_at': u[5]
                }
                for u in users
            ]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'Server is running'}), 200

if __name__ == '__main__':
    init_db()
    print("✅ Database initialized")
    print("🚀 Server starting on http://localhost:5001")
    print("📝 Register endpoint: POST http://localhost:5001/api/register")
    print("🔐 Login endpoint: POST http://localhost:5001/api/login")
    print("👥 Get users endpoint: GET http://localhost:5001/api/users")
    app.run(debug=True, port=5001)
