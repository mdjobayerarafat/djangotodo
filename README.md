# Django REST API + Next.js Todo Application

A full-stack todo application with Django REST API backend and Next.js frontend, featuring asynchronous operations and JWT authentication.

## 🚀 Features

### Backend (Django REST API)
- **Async Views**: High-performance asynchronous API endpoints
- **JWT Authentication**: Secure token-based authentication
- **User Management**: Registration, login, and profile management
- **Todo CRUD**: Create, read, update, delete todos
- **Priority Levels**: Low, medium, high priority todos
- **Due Dates**: Optional due date support
- **CORS Enabled**: Cross-origin requests for frontend integration

### Frontend (Next.js)
- **Modern React**: Built with Next.js 14 and TypeScript
- **Beautiful UI**: Clean, responsive design with Tailwind CSS
- **Authentication**: Login/register with JWT token management
- **Real-time Updates**: Interactive todo management
- **Context API**: Global state management
- **Form Validation**: Client-side form validation

## 📁 Project Structure

```
djangotodo/
├── backend/                 # Django REST API
│   ├── accounts/           # User authentication app
│   ├── todos/              # Todo management app
│   ├── todo_project/       # Django settings
│   ├── manage.py
│   ├── requirements.txt
│   └── venv/               # Virtual environment
├── todo-frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # API utilities
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🛠️ Installation & Setup

### Backend Setup

1. Navigate to the project directory:
   ```bash
   cd djangotodo
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Run migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the Django server:
   ```bash
   python manage.py runserver 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd todo-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env.local
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Todos
- `GET /api/todos/` - List all todos
- `POST /api/todos/` - Create new todo
- `GET /api/todos/{id}/` - Get specific todo
- `PUT /api/todos/{id}/` - Update todo
- `DELETE /api/todos/{id}/` - Delete todo
- `PATCH /api/todos/{id}/toggle/` - Toggle todo completion

## 🔧 Technologies Used

### Backend
- Django 5.2.4
- Django REST Framework 3.16.0
- Django REST Framework SimpleJWT 5.5.1
- Django CORS Headers 4.7.0
- Python Decouple 3.8
- SQLite (development)

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide React (icons)

## 🔒 Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure allowed hosts
3. Use production database (PostgreSQL recommended)
4. Serve static files with whitenoise or CDN
5. Use ASGI server like uvicorn or daphne

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or similar platform
3. Update API URL in environment variables

## 📝 Development Notes

- The Django backend uses async views for better performance
- JWT tokens are automatically handled by the frontend
- CORS is configured to allow requests from the frontend
- The application supports real-time todo updates
- All sensitive data is excluded via .gitignore files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
