

from django.contrib.auth.models import User
from django.db import models
import uuid




class Listing(models.Model):
    PROPERTY_TYPES = [
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('CONDO', 'Condo'),
        ('CABIN', 'Cabin'),
        ('VILLA', 'Villa'),
    ]
    
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    amenities = models.JSONField(default=list)  # ['Wifi', 'Pool', 'Kitchen']
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #ahme..
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
        ]
    
    def __str__(self):
            return f"{self.title} - {self.property_type}"
    
    

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'
        
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name='bookings', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    special_requests = models.TextField(blank=True)
    total_price = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    
    class Meta:
        unique_together = ('user', 'listing', 'start_date', 'end_date')
        ordering = ['-start_date']
        constraints = [models.CheckConstraint(check=models.Q(end_date__gt=models.F('start_date')), name='check_booking_dates')]

    def __str__(self):
        return f"{self.customer_name} booking {self.listing.title}"



class Review(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    listing = models.ForeignKey(Listing, related_name='reviews', on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=255)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer_name} on {self.listing.title}"



class Payment(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Completed, Failed
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chapa_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
