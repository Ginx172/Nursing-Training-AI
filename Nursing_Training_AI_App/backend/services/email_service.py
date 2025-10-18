"""
Email Notification Service
Handles all email communications for the platform
"""

from typing import List, Dict, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@nursingtrainingai.com")
        self.from_name = "Nursing Training AI"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Send email with HTML content"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    self._attach_file(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, attachment: Dict):
        """Attach file to email"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {attachment['filename']}"
            )
            msg.attach(part)
        except Exception as e:
            print(f"Error attaching file: {e}")
    
    # EMAIL TEMPLATES
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = f"Welcome to Nursing Training AI, {user_name}! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0066CC; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; }}
                .button {{ display: inline-block; background: #0066CC; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .features {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .feature-item {{ margin: 10px 0; padding-left: 25px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Welcome to Nursing Training AI!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Welcome to the UK's most comprehensive nursing training platform! We're thrilled to have you join our community of healthcare professionals.</p>
                    
                    <div class="features">
                        <h3>What's included:</h3>
                        <div class="feature-item">✅ 2,140+ question banks covering all UK healthcare sectors</div>
                        <div class="feature-item">✅ 42,800+ questions across all NHS bands (2-8d)</div>
                        <div class="feature-item">✅ AI-powered personalized learning recommendations</div>
                        <div class="feature-item">✅ Audio features (Text-to-Speech & Speech-to-Text)</div>
                        <div class="feature-item">✅ Offline mode for practice anywhere</div>
                        <div class="feature-item">✅ Progress tracking and CPD certificates</div>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="https://app.nursingtrainingai.com/dashboard" class="button">
                            Start Your Training Journey
                        </a>
                    </p>
                    
                    <p>If you have any questions, our support team is here to help at <a href="mailto:support@nursingtrainingai.com">support@nursingtrainingai.com</a></p>
                    
                    <p>Best regards,<br>The Nursing Training AI Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_weekly_report_email(
        self,
        user_email: str,
        user_name: str,
        weekly_summary: Dict
    ) -> bool:
        """Send weekly progress report"""
        subject = f"📊 Your Weekly Training Report - Week Ending {weekly_summary['week_ending']}"
        
        highlights = weekly_summary['highlights']
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0066CC; color: white; padding: 30px; text-align: center; }}
                .stat-box {{ background: #f9f9f9; padding: 20px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #0066CC; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #0066CC; }}
                .achievement {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Progress Report</h1>
                    <p>Week Ending {weekly_summary['week_ending']}</p>
                </div>
                
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Here's your training progress for this week:</p>
                    
                    <div class="stat-box">
                        <div class="stat-value">{highlights['questions_this_week']}</div>
                        <div>Questions Completed</div>
                    </div>
                    
                    <div class="stat-box">
                        <div class="stat-value">{highlights['accuracy_this_week']}%</div>
                        <div>Accuracy This Week</div>
                    </div>
                    
                    <div class="stat-box">
                        <div class="stat-value">{highlights['time_spent_minutes']} min</div>
                        <div>Time Spent Training</div>
                    </div>
                    
                    {'<div class="achievement">🔥 Amazing! You maintained your 7-day streak this week!</div>' if highlights['streak_maintained'] else ''}
                    
                    <h3>🎯 Focus for Next Week:</h3>
                    <p>{weekly_summary['focus_area_next_week']}</p>
                    
                    <p style="margin-top: 30px;">Keep up the excellent work!<br>The Nursing Training AI Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_subscription_confirmation(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        billing_cycle: str
    ) -> bool:
        """Send subscription confirmation email"""
        subject = f"Subscription Confirmed - {plan_name} Plan"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #0066CC;">Thank You for Subscribing! 🎉</h1>
                
                <p>Hi {user_name},</p>
                <p>Your subscription to the <strong>{plan_name}</strong> plan has been confirmed.</p>
                
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Subscription Details:</h3>
                    <p><strong>Plan:</strong> {plan_name}</p>
                    <p><strong>Billing:</strong> {billing_cycle}</p>
                    <p><strong>Amount:</strong> £{amount}</p>
                    <p><strong>Next billing date:</strong> {datetime.now().strftime('%d %B %Y')}</p>
                </div>
                
                <p>You now have full access to all features of your plan!</p>
                
                <p>Best regards,<br>The Nursing Training AI Team</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_payment_failed_email(
        self,
        user_email: str,
        user_name: str,
        amount: float
    ) -> bool:
        """Send payment failed notification"""
        subject = "Payment Failed - Action Required"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #E74C3C;">Payment Failed ⚠️</h1>
                
                <p>Hi {user_name},</p>
                <p>We were unable to process your payment of <strong>£{amount}</strong>.</p>
                
                <p>Please update your payment method to continue enjoying uninterrupted access to Nursing Training AI.</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="https://app.nursingtrainingai.com/billing" style="display: inline-block; background: #0066CC; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">
                        Update Payment Method
                    </a>
                </p>
                
                <p>If you have questions, please contact us at support@nursingtrainingai.com</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_certificate_email(
        self,
        user_email: str,
        user_name: str,
        certificate_title: str,
        certificate_pdf: bytes
    ) -> bool:
        """Send CPD certificate"""
        subject = f"Your CPD Certificate - {certificate_title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #0066CC;">Congratulations! 🎓</h1>
                
                <p>Hi {user_name},</p>
                <p>You've earned a CPD certificate!</p>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #00A651;">Certificate: {certificate_title}</h3>
                    <p>Your certificate is attached to this email.</p>
                </div>
                
                <p>Keep up the excellent work!</p>
                
                <p>Best regards,<br>The Nursing Training AI Team</p>
            </div>
        </body>
        </html>
        """
        
        attachments = [{
            'filename': f'{certificate_title.replace(" ", "_")}.pdf',
            'content': certificate_pdf
        }]
        
        return await self.send_email(user_email, subject, html_content, attachments)

# Singleton instance
email_service = EmailService()

