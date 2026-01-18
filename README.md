# MyWebsite - Registration & Login System

A fully functional registration and login system with frontend and backend integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation & Setup

#### 1. Install Dependencies
```bash
cd /Users/sirinederamchi/Desktop/MyWebsite
pip install -r requirements.txt
```

#### 2. Start the Backend Server
```bash
python server.py
```

You should see:
```
✅ Database initialized
🚀 Server starting on http://localhost:5000
📝 Register endpoint: POST http://localhost:5000/api/register
🔐 Login endpoint: POST http://localhost:5000/api/login
👥 Get users endpoint: GET http://localhost:5000/api/users
```

#### 3. Start the Frontend Server (in another terminal)
```bash
cd /Users/sirinederamchi/Desktop/MyWebsite
python -m http.server 8000
```

#### 4. Open Your Browser
- **Register Page:** `http://localhost:8000/register.html`
- **Login Page:** `http://localhost:8000/login.html`
- **Home Page:** `http://localhost:8000/index.html`

---

## 📋 Features

### Registration (`register.html`)
- ✅ First name validation
- ✅ Last name validation
- ✅ Email validation (unique)
- ✅ Phone number validation (optional)
- ✅ Password validation (min 8 characters)
- ✅ Password confirmation
- ✅ Real-time error messages
- ✅ Saves to SQLite database

### Login (`login.html`)
- ✅ Email validation
- ✅ Password validation
- ✅ Compares against registered users
- ✅ Stores user session in localStorage
- ✅ Redirects to home on success

---

## 🛠️ API Endpoints

### 1. Register User
**POST** `http://localhost:5000/api/register`

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "password": "securePassword123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  }
}
```

---

### 2. Login User
**POST** `http://localhost:5000/api/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  }
}
```

---

### 3. Get All Users (Testing)
**GET** `http://localhost:5000/api/users`

**Response:**
```json
{
  "success": true,
  "count": 2,
  "users": [
    {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "phone": "123-456-7890",
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

---

## 💾 Database

**SQLite Database:** `users.db` (auto-created on first run)

**Table Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 Security Notes

- ✅ Passwords are hashed with SHA-256 before storing
- ✅ Email uniqueness enforced in database
- ✅ CORS enabled for localhost testing
- ✅ Form validation on both frontend and backend

**For Production:**
- Use bcrypt or argon2 instead of SHA-256
- Enable HTTPS
- Add JWT tokens for sessions
- Implement rate limiting
- Use environment variables for secrets

---

## 🧪 Testing

### Test Registration Flow:
1. Go to `http://localhost:8000/register.html`
2. Fill in form with test data
3. Click "REGISTER"
4. Should redirect to login page

### Test Login Flow:
1. Go to `http://localhost:8000/login.html`
2. Use the email and password from registration
3. Click "Sign in"
4. Should redirect to home page

### View All Users (API Testing):
- Open browser: `http://localhost:5000/api/users`

---

## ⚠️ Troubleshooting

### "Error connecting to server"
- Make sure `python server.py` is running on port 5000
- Check that backend terminal shows no errors

### "Email already registered"
- Use a different email address
- Or delete `users.db` to reset the database

### CORS Error
- Flask-CORS is already configured
- Make sure backend server is running

### Database Issues
- Delete `users.db` file to reset
- Database will be recreated on next run

---

## 📁 File Structure
```
MyWebsite/
├── index.html           # Home page
├── login.html           # Login page (updated)
├── register.html        # Registration page (updated)
├── server.py            # Python Flask backend
├── requirements.txt     # Python dependencies
├── users.db             # SQLite database (auto-created)
└── README.md            # This file
```

---

## 📝 Next Steps

1. **Session Management:** Add JWT tokens for better session handling
2. **Email Verification:** Send verification emails on registration
3. **Password Reset:** Implement forgot password functionality
4. **Database:** Switch to PostgreSQL for production
5. **Deployment:** Deploy to Heroku, AWS, or similar

---

Enjoy your website! 🎉
