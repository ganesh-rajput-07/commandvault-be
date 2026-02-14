# PromptDeck Backend - AI Prompt Storage

A comprehensive Django REST API for storing, sharing, and managing AI prompts with social features.

## Features

### Authentication
- Email/password registration and login
- JWT authentication (access + refresh tokens)
- Google OAuth integration
- User profile management
- Account deactivation

### Prompt Management
- Create, read, update, delete prompts
- Public/private prompts
- Auto-tagging and categorization
- Version history tracking
- Search by title, text, and tags

### Social Features
- Like/unlike prompts
- Comment on prompts
- Save/bookmark prompts
- Follow/unfollow users
- Real-time notifications

### Feeds
- Global feed (public prompts + user's private)
- Personal feed (user's prompts)
- Trending feed (sorted by engagement)

### Analytics
- User metrics
- Prompt statistics
- Popular tags
- Most copied/liked prompts

### Moderation
- Report system
- Admin moderation panel
- Soft delete for prompts

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL database in `settings.py`

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/google-login/` - Login with Google
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update profile
- `POST /api/auth/deactivate/` - Deactivate account

### Prompts
- `GET /api/prompts/` - List all prompts
- `POST /api/prompts/` - Create prompt
- `GET /api/prompts/{id}/` - Get prompt details
- `PUT /api/prompts/{id}/` - Update prompt
- `DELETE /api/prompts/{id}/` - Delete prompt
- `GET /api/prompts/mine/` - Get user's prompts
- `GET /api/prompts/trending/` - Get trending prompts
- `GET /api/prompts/search/` - Search prompts
- `POST /api/prompts/{id}/increment_use/` - Increment usage count

### Social Features
- `POST /api/likes/toggle/` - Like/unlike prompt
- `GET /api/likes/my_likes/` - Get user's likes
- `GET /api/comments/` - List comments
- `POST /api/comments/` - Create comment
- `DELETE /api/comments/{id}/` - Delete comment
- `POST /api/saved/toggle/` - Save/unsave prompt
- `GET /api/saved/my_saved/` - Get saved prompts
- `POST /api/follows/toggle/` - Follow/unfollow user
- `GET /api/follows/followers/` - Get followers
- `GET /api/follows/following/` - Get following

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `GET /api/notifications/unread_count/` - Get unread count

### Reports & Moderation
- `POST /api/reports/` - Report a prompt
- `GET /api/reports/` - List reports (admin only)

### Analytics
- `GET /api/analytics/` - Get system analytics (admin only)
- `GET /api/tags/popular/` - Get popular tags

## Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

## Tech Stack
- Django 5.2.9
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Google OAuth 2.0
