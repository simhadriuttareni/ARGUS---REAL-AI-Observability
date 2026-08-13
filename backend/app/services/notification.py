"""
ARGUS Notification Service
Sends alerts via Slack, Email, and Webhooks
"""

from typing import Dict, Any, Optional
import json
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config import settings


class NotificationService:
    """Sends notifications through various channels"""
    
    def __init__(self):
        self.slack_webhook = None
        self.email_config = None
    
    def configure_slack(self, webhook_url: str):
        """Configure Slack webhook"""
        self.slack_webhook = webhook_url
    
    def configure_email(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """Configure email settings"""
        self.email_config = {
            "host": smtp_host,
            "port": smtp_port,
            "username": username,
            "password": password
        }
    
    async def send_slack(self, message: str, attachments: Optional[list] = None):
        """Send a Slack notification"""
        if not self.slack_webhook:
            print("⚠️ Slack webhook not configured")
            return
        
        try:
            payload = {"text": message}
            if attachments:
                payload["attachments"] = attachments
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"❌ Slack error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Slack send error: {e}")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ):
        """Send an email notification"""
        if not self.email_config:
            print("⚠️ Email not configured")
            return
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["To"] = to_email
            msg["From"] = self.email_config["username"]
            
            # Plain text
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)
            
            # HTML (if provided)
            if html:
                html_part = MIMEText(html, "html")
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(
                self.email_config["host"],
                self.email_config["port"]
            ) as server:
                server.starttls()
                server.login(
                    self.email_config["username"],
                    self.email_config["password"]
                )
                server.send_message(msg)
                
        except Exception as e:
            print(f"❌ Email send error: {e}")
    
    async def send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ):
        """Send a webhook notification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers=headers or {},
                    timeout=10.0
                )
                
                if response.status_code not in (200, 201, 202):
                    print(f"❌ Webhook error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Webhook send error: {e}")
    
    async def send_alert(self, alert: Dict[str, Any], channels: list):
        """Send an alert through multiple channels"""
        
        # Format message
        message = self._format_alert_message(alert)
        
        # Send to each channel
        for channel in channels:
            if channel == "slack" and self.slack_webhook:
                await self.send_slack(message)
            elif channel == "email" and self.email_config:
                await self.send_email(
                    to_email=alert.get("recipient", "admin@example.com"),
                    subject=f"[ARGUS Alert] {alert.get('severity', 'info')}: {alert.get('rule_name', 'Unknown')}",
                    body=message
                )
    
    def _format_alert_message(self, alert: Dict[str, Any]) -> str:
        """Format alert message for display"""
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        emoji = severity_emoji.get(alert.get("severity", "info"), "🔔")
        
        return f"""
{emoji} *ALERT: {alert.get('rule_name', 'Unknown')}*

*Severity:* {alert.get('severity', 'info')}
*Model:* {alert.get('model', 'unknown')}
*Provider:* {alert.get('provider', 'unknown')}
*Reason:* {alert.get('reason', 'No reason provided')}
*Time:* {alert.get('created_at', 'unknown')}

{alert.get('data', {})}
        """


# Singleton instance
notification_service = NotificationService()