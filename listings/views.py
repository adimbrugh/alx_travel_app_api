

from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
from .payment_utilty import initiate_chapa_payment, CHAPA_VERIFY_URL
from rest_framework import viewsets, permissions, status
from .models import Listing, Booking, Review, Payment
from .tasks import send_booking_confirmation_email
from rest_framework.response import Response
from rest_framework.views import APIView
from alx_travel_app import settings
import requests




class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        booking = serializer.save()
        user_email = booking.user.email
        send_booking_confirmation_email.delay(user_email, booking.id)



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class InitiatePaymentView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            
            # Check if payment already exists
            if hasattr(booking, 'payment'):
                return Response(
                    {"error": "Payment already initiated for this booking"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initiate payment with Chapa
            payment_response = initiate_chapa_payment(booking, request)
            
            if not payment_response or 'status' not in payment_response or payment_response['status'] != 'success':
                return Response(
                    {"error": "Failed to initiate payment"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                transaction_id=payment_response['data']['tx_ref'],
                chapa_response=payment_response
            )
            
            return Response({
                "status": "success",
                "checkout_url": payment_response['data']['checkout_url'],
                "transaction_id": payment.transaction_id
            })
            
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
            

class VerifyPaymentView(APIView):
    def get(self, request):
        transaction_id = request.query_params.get('tx_ref')
        
        if not transaction_id:
            return Response(
                {"error": "Transaction reference required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            
            # Verify with Chapa API
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
            }
            
            verify_url = f"{CHAPA_VERIFY_URL}{transaction_id}"
            response = requests.get(verify_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    payment.status = 'completed'
                    payment.chapa_response = data
                    payment.save()
                    
                    # Trigger confirmation email (Celery task)
                    #send_booking_confirmation.delay(payment.booking.id)
                    send_booking_confirmation_email.delay(payment.booking.user.email, payment.booking.id)   
                    
                    return Response({"status": "completed"})
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({"status": "failed"})
            
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_502_BAD_GATEWAY
            )
            
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )