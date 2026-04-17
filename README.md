
# Chemical Equipment Parameter Visualizer

A hybrid web and desktop application for visualizing, analyzing, and
reporting chemical equipment parameters using CSV datasets.

------------------------------------------------------------------------

## 🎯 Project Overview

The Chemical Equipment Parameter Visualizer is a full-stack hybrid
system where:

-   A Django REST backend manages data and authentication
-   A React.js web frontend provides interactive visualization
-   A PyQt5 desktop client offers native access

The system enables engineers and analysts to upload CSV files, visualize
equipment parameters, generate reports, and maintain upload history.

This project was developed as part of an internship screening task.

------------------------------------------------------------------------

## 🛠️ Tech Stack

  Layer             Technology
  ----------------- -------------------------------
  Backend           Django, Django REST Framework
  Web Frontend      React.js, Chart.js, Axios
  Desktop Client    PyQt5, Matplotlib
  Data Processing   Pandas
  Database          SQLite
  Reporting         ReportLab, openpyxl
  Version Control   Git, GitHub

------------------------------------------------------------------------

## ✨ Features

### Core Features

-   CSV file upload (Web & Desktop)
-   Automatic data summary
-   Interactive charts
-   PDF report generation
-   Excel export
-   Upload history (Last 5 datasets)
-   Token-based authentication
-   User data isolation

### UI Features

-   Dark mode (Web)
-   Search and filter
-   Smooth animations
-   Responsive layout
-   Loading indicators

------------------------------------------------------------------------

## 📁 Project Structure

    chemical-equipment-visualizer/
    ├── backend/
    │   ├── api/
    │   ├── config/
    │   ├── db.sqlite3
    │   ├── manage.py
    │   └── requirements.txt
    │
    ├── frontend/
    │   ├── src/
    │   ├── public/
    │   ├── package.json
    │   └── package-lock.json
    │
    ├── desktop/
    │   ├── main.py
    │   └── requirements.txt
    │
    ├── README.md
    └── .gitignore

------------------------------------------------------------------------

## 🚀 Setup Instructions

### Prerequisites

-   Python 3.9+
-   Node.js 16+
-   Git

------------------------------------------------------------------------

## Backend Setup

``` bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Server runs at:

    http://localhost:8000

------------------------------------------------------------------------

## Web Frontend Setup

``` bash
cd frontend
npm install
npm start
```

Runs at:

    http://localhost:3000

------------------------------------------------------------------------

## Desktop Application Setup

``` bash
cd desktop
pip install -r requirements.txt
python main.py
```

⚠️ Backend must be running before launching desktop app.

------------------------------------------------------------------------

## 📖 Usage Guide

### Step 1: Start Backend

``` bash
python manage.py runserver
```

### Step 2: Start Client

Choose one:

Web:

``` bash
npm start
```

Desktop:

``` bash
python main.py
```

### Step 3: Login / Register

Create account or login.

### Step 4: Upload CSV

Select file and click Upload.

### Step 5: View Analytics

-   Summary cards
-   Pie charts
-   Bar charts
-   Equipment table

### Step 6: Generate Reports

-   Download PDF
-   Export Excel

### Step 7: View History

Reload previous uploads.

------------------------------------------------------------------------

## 📋 CSV File Format

Required columns:

  Column           Type     Description
  ---------------- -------- --------------
  Equipment Name   String   Equipment ID
  Type             String   Category
  Flowrate         Float    Flow
  Pressure         Float    Pressure
  Temperature      Float    Temperature

### Example

``` csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A,Centrifugal,150.5,45.2,85.0
Heat-Exchanger-B,Shell-Tube,200.0,30.5,120.5
Reactor-C,CSTR,175.3,50.0,95.7
```

------------------------------------------------------------------------

## 🔌 API Endpoints

  Method   Endpoint                Description
  -------- ----------------------- ----------------
  POST     /api/auth/register/     Register
  POST     /api/auth/login/        Login
  POST     /api/upload/            Upload CSV
  GET      /api/summary/           Data Summary
  GET      /api/equipment/         Equipment List
  GET      /api/history/           Upload History
  POST     /api/generate-report/   PDF Report
  POST     /api/export-excel/      Excel Export

Authorization Header:

    Authorization: Token <your_token>

------------------------------------------------------------------------

## 🗄️ Database Models

### UploadHistory

-   id
-   filename
-   uploaded_at
-   total_count
-   avg_flowrate
-   avg_pressure
-   avg_temperature
-   user

### Equipment

-   id
-   upload_history
-   equipment_name
-   equipment_type
-   flowrate
-   pressure
-   temperature

------------------------------------------------------------------------

## 🔒 Security Features

-   Token authentication
-   Password hashing
-   CSRF protection
-   Django ORM protection
-   Permission-based access
-   User data isolation

------------------------------------------------------------------------

## 🐛 Troubleshooting

### Backend Errors

``` bash
pip install -r requirements.txt
python manage.py migrate
```

### Frontend Errors

``` bash
npm cache clean --force
npm install
```

### Desktop Errors

``` bash
pip install PyQt5
```

------------------------------------------------------------------------

## 📊 Performance

-   Handles large CSV files
-   Optimized database queries
-   Lazy loading
-   Cached summaries
-   Efficient filtering

------------------------------------------------------------------------

## 🚀 Future Enhancements

-   JSON/XML export
-   Dataset comparison
-   Email reports
-   Cloud storage
-   Multi-language support
-   Real-time collaboration
-   Mobile app

------------------------------------------------------------------------

## 📝 Development Notes

### Sample Upload Response

``` json
{
  "message": "File uploaded successfully",
  "upload_id": 1,
  "summary": {
    "total_count": 100,
    "avg_flowrate": 175.5,
    "avg_pressure": 42.3,
    "avg_temperature": 95.7
  }
}
```

------------------------------------------------------------------------

## 👨‍💻 Author

**Siri V Hegde**\
VTU CSE Student\
Mysuru, Karnataka, India

------------------------------------------------------------------------

## 📄 License

MIT License

------------------------------------------------------------------------

## 🙏 Acknowledgments

-   IIT Bombay
-   Django Community
-   React Community
-   Open Source Contributors

------------------------------------------------------------------------

## 📞 Support

For help:

1.  Check logs
2.  Verify setup
3.  Install dependencies
4.  Restart services

------------------------------------------------------------------------

**Built with ❤️ for Internship Screening Project**
=======
# chemical-equipment-visualizer
Hybrid Web + Desktop App for Chemical Equipment Visualization - IIT Bombay Internship Task
>>>>>>> e8eec220cab7f9c334505038512dde72c32a219a
