# Job Board Backend (Project Nexus) 🚀

The Job Board Backend is a real-world application developed as part of Project Nexus in the ALX ProDev Backend Program.

A comprehensive RESTful API for a modern job board platform built with Django REST Framework. Supports role-based authentication, advanced job search, and complete application workflow management.

---

## 🚀 Features

- **Role-Based Authentication**: Job Seeker, Employer, and Admin roles with JWT tokens
- **Advanced Job Search**: Filter by categories, skills, location, job type, and salary range
- **Company Management**: Multi-user company profiles with manager permissions
- **Application Workflow**: Complete job application pipeline with status tracking
- **Admin Dashboard**: Comprehensive administrative controls and analytics
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Performance Optimized**: Database indexing and query optimization

---

## 🛠️  Technology Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT with Simple JWT
- **API Documentation**: DRF Spectacular (Swagger/OpenAPI)
- **File Storage**: Django Storage for resumes and company logos
- **Filtering**: Django Filter with advanced search capabilities

---

## ⚙️ Installation

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

4. **Environment Configuration:**
- Create a **.env** file in the project root:
```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=nexus_jobboard
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

5. **Set Up Database:**
- Create a PostgreSQL database
```bash
# Create PostgreSQL database
createdb nexus_jobboard

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Run the Server:**
```bash
python manage.py runserver
```

---

##  📚 API Documentation

Interactive Documentation:
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

---

##  🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **User Registration:**
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "employer1",
  "email": "employer@company.com",
  "password": "securepassword123",
  "password_confirmation": "securepassword123",
  "user_type": "employer",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

2. **User Login:**
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "employer1",
  "password": "securepassword123"
}
```
    Response includes access and refresh tokens:
```bash
{
  "user": { ... },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

3. **Using Access Tokens:**
    Include the token in request headers:
```bash
Authorization: Bearer your-access-token-here
```

---

##  👥 User Roles

Job Seeker:
- Browse and search jobs
- Apply to jobs
- Manage own applications
- Update personal profile

Employer:
- Create and manage company profile
- Post and manage job listings
- Review applications
- Update application status

Admin:
- Full system access
- Manage all users, companies, jobs
- System analytics and reporting

---

##  🗃️ Core Endpoints

Authentication:
- `POST /api/auth/register/ ` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - User profile

Jobs:
- `GET /api/jobs/` - List all active jobs
- `POST /api/jobs/` - Create new job (Employer/Admin)
- `GET /api/jobs/search/` - Advanced job search
- `GET /api/jobs/{id}/` - Job details
- `PUT /api/jobs/{id}/` - Update job (Owner/Manager/Admin)
- `DELETE /api/jobs/{id}/` - Delete job (Owner/Manager/Admin)

Applications:
- `GET /api/applications/` - User's applications
- `POST /api/applications/` - Apply to job (Job Seeker)
- `GET /api/applications/job/{job_id}/` - Job applications (Employer/Admin)
- `PATCH /api/applications/{id}/status/` - Update application status

Companies:
- `GET /api/companies/` - List all companies
- `POST /api/companies/` - Create company (Authenticated users)
- `GET /api/companies/{id}/` - Company details
- `POST /api/companies/{id}/managers/add/` - Add manager (Owner/Admin)

Categories & Skills:
- `GET /api/categories/` - List all categories
- `GET /api/skills/` - List all skills
- `GET /api/categories/with-jobs/` - Categories with active jobs
Admin Endpoints:
- `GET /api/users/admin/users/` - List all users
- `GET /api/jobs/admin/all/` - List all jobs (including inactive)
- `GET /api/applications/admin/all/` - List all applications
- `PATCH /api/users/admin/users/{id}/activation/` - Activate/deactivate users

---

##  📊 Example Workflows

Job Seeker Workflow:
1. Register as `job_seeker`
2. Browse jobs at `GET /api/jobs/`
3. Search for specific roles `GET /api/jobs/search/?title=developer`
4. Apply to job `POST /api/applications/`
5. Track applications `GET /api/applications/my-applications/`

Employer Workflow:
1. Register as `employer`
2. Create company `POST /api/companies/`
3. Post job `POST /api/jobs/`
4. Review applications `GET /api/applications/job/{job_id}/`
5. Update application status `PATCH /api/applications/{id}/status/`

---

