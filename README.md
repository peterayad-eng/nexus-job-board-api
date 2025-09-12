# Job Board Backend (Project Nexus) 🚀

The Job Board Backend is a real-world application developed as part of Project Nexus in the ALX ProDev Backend Program.

It provides a robust backend system for a job board platform, featuring role-based access control, secure authentication, optimized job search, and comprehensive API documentation.

This project demonstrates industry best practices in backend development, database optimization, and API design, preparing the foundation for scalable and production-ready systems.

---

## 🎯 Project Goals

- **Job Posting Management:** CRUD APIs for managing job postings, categories, and job applications
- **Access Control:** Role-based authentication for admins and regular users using JWT
- **Application Tracking:** Complete application workflow management
- **API Documentation:** Integrated Swagger documentation for easy frontend consumption

---

## 🛠️ Technology Stack

- **Backend Framework:** Django & Django REST Framework
- **Database:** PostgreSQL with advanced indexing
- **Authentication:** JWT to secure role-based authentication
- **Documentation:** Swagger for Interactive API documentation

---

## 🚀 Getting Started

1. **Clone the Repository:** 
```bash
git clone https://github.com/peterayad-eng/nexus-job-board-api.git
cd nexus-job-board-api
```

2. **Create and Activate Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set Up Database:**
- Create a PostgreSQL database and update the settings in settings.py

5. **Run Migrations:**
```bash
python manage.py migrate
```

6. **Start the Server:**
```bash
python manage.py runserver
```

---

