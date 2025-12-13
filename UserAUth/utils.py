import secrets
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone


def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(user):
    """Send email verification link to user"""
    # Generate token
    token = generate_verification_token()
    user.email_verification_token = token
    user.email_verification_sent_at = timezone.now()
    user.save()
    
    # Create verification URL
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    # Email subject
    subject = 'Verify your CommandVault email'
    
    # Email body (HTML)
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                border-radius: 16px;
                text-align: center;
            }}
            .content {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                margin-top: 20px;
            }}
            h1 {{
                color: white;
                margin: 0;
                font-size: 32px;
                font-weight: 800;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            p {{
                color: #666;
                font-size: 16px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                padding: 16px 32px;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
            }}
            .footer {{
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                margin-top: 20px;
            }}
            .expiry {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 12px;
                margin: 20px 0;
                border-radius: 4px;
                color: #92400e;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚀</div>
            <h1>CommandVault</h1>
            <div class="content">
                <h2>Welcome to CommandVault!</h2>
                <p>Hi {user.username},</p>
                <p>Thank you for signing up! Please verify your email address to get started with CommandVault.</p>
                <a href="{verification_url}" class="button">Verify Email Address</a>
                <div class="expiry">
                    ⏰ This link will expire in 24 hours
                </div>
                <p style="font-size: 14px; color: #999;">
                    If you didn't create an account, you can safely ignore this email.
                </p>
                <p style="font-size: 12px; color: #999; margin-top: 30px;">
                    Or copy and paste this URL into your browser:<br>
                    <span style="word-break: break-all;">{verification_url}</span>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 CommandVault. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"""
    Welcome to CommandVault!
    
    Hi {user.username},
    
    Thank you for signing up! Please verify your email address by clicking the link below:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, you can safely ignore this email.
    
    © 2024 CommandVault
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    return True
