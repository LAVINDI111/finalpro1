# ACNSMS - Automated Campus Notification and Schedule Management System

A comprehensive web-based platform for managing campus schedules, notifications, and communication in educational institutions.

## Features

- **Real-time Notifications**: Automated email and SMS notifications for schedule changes
- **Smart Scheduling**: AI-powered scheduling suggestions and conflict detection
- **Google Calendar Integration**: Seamless synchronization with Google Calendar
- **Role-based Access Control**: Separate interfaces for students, lecturers, and administrators
- **Responsive Design**: Mobile-friendly interface built with Bootstrap 5
- **Secure Authentication**: Encrypted passwords and session management

## Technology Stack

- **Backend**: Python Flask
- **Database**: MariaDB
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Calendar**: Google Calendar API
- **Notifications**: Email (SMTP), SMS (Twilio)
- **Analytics**: PowerBI integration ready

## Installation

### Prerequisites

- Python 3.8+
- MariaDB
- Google Calendar API credentials
- Twilio account (for SMS)
- Gmail account (for email notifications)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd acnsms
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MariaDB database**
   ```sql
   CREATE DATABASE acnsms;
   CREATE USER 'acnsms_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON acnsms.* TO 'acnsms_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update the configuration with your credentials:
   ```
   DATABASE_URL=mysql+pymysql://acnsms_user:your_password@localhost/acnsms
   SECRET_KEY=your-secret-key-here
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-number
   ```

6. **Set up Google Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create credentials (OAuth 2.0 client ID)
   - Download `credentials.json` and place it in the project root

7. **Initialize the database**
   ```bash
   python database_setup.py
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

9. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Use the sample credentials provided in the setup output

## Configuration

### Email Setup (Gmail)
1. Enable 2-factor authentication in your Gmail account
2. Generate an app password: Gmail Settings > Security > App passwords
3. Use the app password in your `.env` file

### SMS Setup (Twilio)
1. Create a Twilio account
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Add the credentials to your `.env` file

### Google Calendar Setup
1. Follow the Google Calendar API setup steps above
2. Run the application and complete the OAuth flow
3. The system will automatically sync schedules with your calendar

## Usage

### For Students
- View your class schedule
- Receive automatic notifications for schedule changes
- Access course information and enrolled modules

### For Lecturers
- Create and manage class schedules
- Reschedule classes with automatic notifications
- View student enrollment information

### For Administrators
- Manage all schedules and users
- Monitor system notifications
- Generate reports and analytics

## Project Structure

```
acnsms/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database_setup.py      # Database initialization script
├── requirements.txt       # Python dependencies
├── services/
│   ├── notification_service.py  # Email/SMS service
│   └── calendar_service.py      # Google Calendar service
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard_*.html   # Role-specific dashboards
│   ├── create_schedule.html
│   └── reschedule.html
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── main.js        # JavaScript functionality
└── .env.example           # Environment variables template
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Schedules
- `GET /api/schedules` - Get all schedules (JSON)
- `POST /schedule/create` - Create new schedule
- `POST /schedule/reschedule/<id>` - Reschedule existing class

### Dashboard
- `GET /dashboard` - Role-specific dashboard

## Database Schema

### Users
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `phone`
- `password_hash`
- `role` (student/lecturer/admin)
- `created_at`
- `is_active`

### Modules
- `id` (Primary Key)
- `module_code` (Unique)
- `module_name`
- `lecturer_id` (Foreign Key)
- `credits`
- `description`
- `created_at`

### Schedules
- `id` (Primary Key)
- `module_id` (Foreign Key)
- `classroom`
- `date`
- `start_time`
- `end_time`
- `status`
- `google_event_id`
- `created_at`
- `updated_at`

### Notifications
- `id` (Primary Key)
- `schedule_id` (Foreign Key)
- `user_id` (Foreign Key)
- `notification_type` (email/sms)
- `status` (pending/sent/failed)
- `message`
- `sent_at`
- `created_at`

## Security Features

- Password hashing with bcrypt
- Session management
- CSRF protection
- Input validation
- SQL injection prevention
- XSS protection

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MariaDB is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **Google Calendar API Error**
   - Check `credentials.json` is in project root
   - Verify API is enabled in Google Cloud Console
   - Complete OAuth flow

3. **Email/SMS Not Working**
   - Verify SMTP settings
   - Check Twilio credentials
   - Ensure phone numbers include country code

### Logs
- Application logs are printed to console
- Check for error messages and stack traces
- Enable debug mode for detailed error information

## Development

### Adding New Features
1. Update database models in `app.py`
2. Create migration scripts if needed
3. Add new routes and templates
4. Update frontend JavaScript if required
5. Test thoroughly before deployment

### Testing
- Run the application in development mode
- Test all user roles and permissions
- Verify notification delivery
- Check calendar synchronization

## Deployment

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up SSL/HTTPS
4. Configure proper database backups
5. Set up monitoring and logging

### Environment Variables for Production
```
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://user:password@host/database
SECRET_KEY=secure-random-key
SESSION_COOKIE_SECURE=True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed as part of an internship at Knock to Smart (Pvt) Ltd.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments
- Create an issue in the repository

## Future Enhancements

- Mobile app development
- Advanced analytics dashboard
- Integration with other calendar systems
- Automated attendance tracking
- Resource booking system
- Multi-language support