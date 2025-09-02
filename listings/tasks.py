

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .models import Booking
import datetime




@shared_task
def send_booking_confirmation_email(user_email, booking_id):
    subject = "Booking Confirmation"
    message = f"Your booking with ID {booking_id} has been confirmed."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    return f"Email sent to {user_email} for booking {booking_id}"



@shared_task
def send_booking_reminder_email():
    bookings = Booking.objects.filter(status='confirmed')
    for booking in bookings:
        subject = "Booking Reminder"
        html_message = render_to_string('emails/booking_reminder.html', {'booking': booking})
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    return f"email reminders sent to {bookings.count()} users with confirmed bookings"



@shared_task
def send_booking_cancellation_email(user_email, booking_id):
    subject = "Booking Cancellation"
    message = f"Your booking with ID {booking_id} has been cancelled."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    return f"Cancellation email sent to {user_email} for booking {booking_id}"



@shared_task
def send_weekly_newsletter():
    # Logic to send weekly newsletter to all users
    # This is a placeholder implementation
    subject = "Weekly Newsletter"
    message = "Here are the latest updates from ALX Travel."
    recipient_list = [user.email for user in User.objects.all()]
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
    return f"Weekly newsletter sent to {len(recipient_list)} users"



@shared_task
def cleanup_expired_bookings():
    expired_bookings = Booking.objects.filter(status='pending', end_date__lt=datetime.date.today())
    count = expired_bookings.count()
    expired_bookings.delete()
    return f"Cleaned up {count} expired bookings" 

