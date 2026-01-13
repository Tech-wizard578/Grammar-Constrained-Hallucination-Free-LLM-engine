"""Contact form routes for the Hallucination-Free Engine API."""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr

router = APIRouter()

# Path to store contact messages
MESSAGES_FILE = Path("./contact_messages.json")


class ContactMessage(BaseModel):
    """Contact form submission model."""
    name: str
    email: EmailStr
    message: str


class ContactMessageResponse(BaseModel):
    """Response model for contact message."""
    id: str
    name: str
    email: str
    message: str
    timestamp: str
    email_sent: bool


class ContactMessagesListResponse(BaseModel):
    """Response model for listing messages."""
    messages: List[ContactMessageResponse]
    total: int


def load_messages() -> List[dict]:
    """Load messages from JSON file."""
    if MESSAGES_FILE.exists():
        try:
            with open(MESSAGES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_messages(messages: List[dict]):
    """Save messages to JSON file."""
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def send_email_notification(name: str, email: str, message: str) -> bool:
    """
    Send email notification for new contact message.
    
    Requires environment variables:
    - SMTP_HOST: SMTP server host (e.g., smtp.gmail.com)
    - SMTP_PORT: SMTP server port (e.g., 587)
    - SMTP_USER: SMTP username/email
    - SMTP_PASSWORD: SMTP password (app password for Gmail)
    - CONTACT_EMAIL: Email to receive contact form submissions
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    contact_email = os.getenv("CONTACT_EMAIL", "aasheerwad009@gmail.com")
    
    # If SMTP not configured, skip email
    if not all([smtp_host, smtp_user, smtp_password]):
        print("⚠️ SMTP not configured, skipping email notification")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = contact_email
        msg["Subject"] = f"New Contact Form Submission from {name}"
        
        body = f"""
You have received a new message from your website contact form.

Name: {name}
Email: {email}

Message:
{message}

---
Sent from HallucinationFree.ai Contact Form
        """
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email notification sent to {contact_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


@router.post("/contact", response_model=ContactMessageResponse)
async def submit_contact_form(
    contact: ContactMessage,
    background_tasks: BackgroundTasks
):
    """
    Submit a contact form message.
    
    - Stores the message in a JSON file
    - Sends email notification (if SMTP configured)
    """
    # Generate message ID
    message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(contact.email) % 10000}"
    timestamp = datetime.now().isoformat()
    
    # Create message record
    message_record = {
        "id": message_id,
        "name": contact.name,
        "email": contact.email,
        "message": contact.message,
        "timestamp": timestamp,
        "email_sent": False
    }
    
    # Save message
    messages = load_messages()
    messages.insert(0, message_record)
    save_messages(messages)
    
    print(f"📬 New contact message from {contact.name} ({contact.email})")
    
    # Send email in background
    def send_email_task():
        success = send_email_notification(contact.name, contact.email, contact.message)
        if success:
            # Update message record
            msgs = load_messages()
            for msg in msgs:
                if msg["id"] == message_id:
                    msg["email_sent"] = True
                    break
            save_messages(msgs)
    
    background_tasks.add_task(send_email_task)
    
    return ContactMessageResponse(**message_record)


@router.get("/contact/messages", response_model=ContactMessagesListResponse)
async def get_contact_messages(limit: int = 50, offset: int = 0):
    """
    Get all contact form messages (admin endpoint).
    """
    messages = load_messages()
    paginated = messages[offset:offset + limit]
    
    return ContactMessagesListResponse(
        messages=[ContactMessageResponse(**msg) for msg in paginated],
        total=len(messages)
    )


@router.delete("/contact/messages/{message_id}")
async def delete_contact_message(message_id: str):
    """
    Delete a contact message by ID.
    """
    messages = load_messages()
    original_count = len(messages)
    messages = [m for m in messages if m["id"] != message_id]
    
    if len(messages) == original_count:
        raise HTTPException(status_code=404, detail="Message not found")
    
    save_messages(messages)
    return {"status": "deleted", "id": message_id}
