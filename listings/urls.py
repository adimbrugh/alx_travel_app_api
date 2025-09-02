


from .views import ListingViewSet, BookingViewSet, ReviewViewSet, InitiatePaymentView, VerifyPaymentView
from rest_framework.routers import DefaultRouter
from django.urls import path, include




router = DefaultRouter()
router.register(r'listing', ListingViewSet)
router.register(r'booking', BookingViewSet)
router.register(r'reviews', ReviewViewSet)  


#payment_view = InitiatePaymentView.as_view({'post': 'initiate_payment'})
#verify_view = InitiatePaymentView.as_view({'get': 'verify_payment'})


urlpatterns = [
    path('', include(router.urls)),
    path('payment/initiate/<int:booking_id>/', InitiatePaymentView.as_view, name='initiate-payment'),
    path('payment/verify/<str:tx_ref>/', VerifyPaymentView.as_view, name='verify-payment'),
]
