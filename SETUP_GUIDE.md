# Missing Person Tracking System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- MySQL Server
- pip (Python package manager)
- npm (Node package manager)

---

## 📦 STEP 1: Backend Setup

### 1.1 Install Python Dependencies
```bash
cd missing_person_ai_backend
pip install -r requirements.txt
```

### 1.2 Setup MySQL Database

**Option A: Using MySQL Command Line**
```bash
mysql -u root -p < database/setup_database.sql
```

**Option B: Using MySQL Workbench**
1. Open MySQL Workbench
2. Connect to your MySQL server
3. Open `database/setup_database.sql`
4. Execute the script

### 1.3 Configure Database Connection

Edit `app.py` line 36-39 with your MySQL credentials:
```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",  # Change this
        database="missing_person_ai"
    )
```

### 1.4 Start Backend Server
```bash
uvicorn app:app --reload --port 8000
```

Backend will run at: **http://127.0.0.1:8000**

---

## 💻 STEP 2: Frontend Setup

### 2.1 Install Node Dependencies
```bash
cd missing-person-frontend
npm install
```

### 2.2 Start Angular Development Server
```bash
ng serve
```

Frontend will run at: **http://localhost:4200**

---

## 🧪 STEP 3: Test the System

### 3.1 Test Backend APIs

Open browser and test:
- http://127.0.0.1:8000/docs (FastAPI Swagger UI)
- http://127.0.0.1:8000/api/all-cases (Get all cases)
- http://127.0.0.1:8000/stations (Get police stations)

### 3.2 Test Frontend

1. Open http://localhost:4200
2. Navigate to "Report Missing Person"
3. Fill the form and upload an image
4. Submit and check for success message
5. Go to "View Missing Persons" to see the data

---

## 📁 Project Structure

```
final year project/
├── missing_person_ai_backend/
│   ├── app.py                    # Main FastAPI application
│   ├── database/
│   │   └── setup_database.sql    # Database setup script
│   ├── uploads/                   # Uploaded images stored here
│   └── requirements.txt           # Python dependencies
│
└── missing-person-frontend/
    ├── src/
    │   ├── app/
    │   │   ├── services/
    │   │   │   └── auth.service.ts    # API service
    │   │   ├── pages/
    │   │   │   ├── report-missing/    # Report form
    │   │   │   ├── view-missing/      # View cases
    │   │   │   └── ai-recognition/    # Face recognition
    │   │   └── app.routes.ts          # Routes
    │   └── styles.css                 # Global styles
    └── package.json
```

---

## 🔧 Common Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'uvicorn'
**Solution:**
```bash
pip install uvicorn
```

### Issue 2: MySQL Connection Error
**Solution:**
1. Ensure MySQL server is running
2. Check username/password in `app.py`
3. Verify database exists: `SHOW DATABASES;`

### Issue 3: CORS Error in Frontend
**Solution:**
Backend already has CORS enabled. Check if backend is running on port 8000.

### Issue 4: Image Not Uploading
**Solution:**
1. Check `uploads/` folder exists in backend
2. Ensure file field name is 'file' in FormData
3. Check browser console for errors

### Issue 5: Angular Compilation Errors
**Solution:**
```bash
npm install
ng serve
```

---

## 🎨 Features Implemented

✅ Report missing person with image upload  
✅ Face encoding and storage  
✅ View all missing persons  
✅ OTP-based case tracking  
✅ FIR submission  
✅ Police dashboard  
✅ CCTV frame capture  
✅ AI face recognition  
✅ Professional police theme UI  
✅ Responsive design  

---

## 📸 Image Upload Flow

1. User selects image in form
2. Frontend creates FormData with 'file' field
3. Backend receives image via FastAPI UploadFile
4. Image saved to `uploads/` folder
5. Face encoding extracted using face_recognition
6. Encoding stored in database as string
7. Image URL returned to frontend

---

## 🔐 API Endpoints

### Authentication
- POST `/police/signup` - Register police user
- POST `/police/login` - Login police user

### Missing Persons
- POST `/api/missing` - Report missing person (with image)
- GET `/api/all-cases` - Get all missing persons
- PUT `/api/update-case/{id}` - Update case status

### OTP
- POST `/send-otp` - Send OTP to mobile
- POST `/verify-otp` - Verify OTP and get cases

### FIR
- POST `/api/fir` - Submit FIR
- GET `/api/fir` - Get all FIRs

### CCTV/Face Recognition
- POST `/api/save-frame` - Save CCTV frame
- GET `/api/frames` - Get all frames
- POST `/detect-image` - Detect face match
- GET `/auto-detect` - Auto detect all frames

---

## 🎯 Testing Checklist

- [ ] Backend starts without errors
- [ ] Database tables created successfully
- [ ] Frontend compiles without errors
- [ ] Report missing person form works
- [ ] Image uploads and saves correctly
- [ ] Face encoding generated (check console)
- [ ] View missing persons displays data
- [ ] Images display correctly in table
- [ ] OTP sending works
- [ ] FIR submission works
- [ ] Police login/signup works
- [ ] AI face recognition works
- [ ] No console errors in browser
- [ ] UI is responsive on mobile

---

## 📞 Support

For issues or questions:
1. Check console logs (backend terminal)
2. Check browser console (F12)
3. Verify database connection
4. Ensure both servers are running

---

## 🎓 Project Info

**Project Name:** Missing Person Tracking System  
**Technology Stack:** 
- Frontend: Angular 21, TypeScript, Material Design
- Backend: FastAPI, Python, MySQL
- AI: face_recognition, numpy

**Developed for:** Final Year Project

---

**Happy Coding! 🚔**
