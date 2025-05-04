# Learning Management System (LMS) Backend

This is the backend for a Learning Management System built with Django and Django REST Framework.

## Features

- User Management (Admin and Manager roles)
- Institute Management
- Teacher Management
- Student Management
- Classroom Management
- Subject Management
- Chapter Management
- Assignment Management
- Submission Management

## Prerequisites

- Python 3.8+
- MySQL
- Virtual Environment (recommended)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd lms_backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create MySQL database:
```sql
CREATE DATABASE lms_db;
```

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the database credentials and other settings in `.env`

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

The API is available at `http://localhost:8000/api/`

### Authentication
- Login: `POST /api/token/`
- Refresh Token: `POST /api/token/refresh/`

### Main Endpoints

- Addresses: `/api/addresses/`
- Institutes: `/api/institutes/`
- Users: `/api/users/`
- Subjects: `/api/subjects/`
- Teachers: `/api/teachers/`
- Teacher Subjects: `/api/teacher-subjects/`
- Classrooms: `/api/classrooms/`
- Students: `/api/students/`
- Class Subjects: `/api/class-subjects/`
- Chapters: `/api/chapters/`
- Enrollments: `/api/enrollments/`
- Assignments: `/api/assignments/`
- Submissions: `/api/submissions/`

## Frontend Integration

The backend is designed to work with a React frontend. The API endpoints follow RESTful conventions and return JSON responses.

## Security

- JWT Authentication
- Role-based access control
- Institute-based data isolation
- Password hashing
- CORS configuration

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 

## GraphQL Integration

This project uses GraphQL for API communication between the frontend and backend. Here's how to set it up and use it:

### Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a test teacher for development:
   ```bash
   python manage.py create_test_teacher
   ```

3. Run the development server:
   ```bash
   python manage.py runserver
   ```

4. Access the GraphQL playground at http://localhost:8000/graphql/

### Authentication

The GraphQL API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Use the `teacherLogin` mutation:
   ```graphql
   mutation {
     teacherLogin(email: "teacher@example.com", password: "password") {
       success
       token
       teacher {
         id
         name
         email
         teacherCode
         institute {
           id
           name
         }
       }
       error
     }
   }
   ```

2. Use the returned token in the Authorization header for subsequent requests:
   ```
   Authorization: Bearer <token>
   ```

### Available Queries and Mutations

#### Queries

- `me`: Get the current authenticated user
- `users`: Get all users (requires authentication)
- `teacher(email: String!)`: Get a teacher by email

#### Mutations

- `teacherLogin(email: String!, password: String!)`: Login as a teacher
- `createUser(username: String!, email: String!, password: String!, firstName: String, lastName: String)`: Create a new user
- `tokenAuth(username: String!, password: String!)`: Obtain a JWT token
- `verifyToken(token: String!)`: Verify a JWT token
- `refreshToken(token: String!)`: Refresh a JWT token

### Frontend Integration

The frontend React application is configured to use Apollo Client for GraphQL communication. The authentication flow is handled in the `AuthContext.tsx` file.

To test the teacher login:
1. Start the backend server
2. Start the frontend development server
3. Navigate to the teacher login page
4. Use the test credentials:
   - Email: teacher@example.com
   - Password: password 