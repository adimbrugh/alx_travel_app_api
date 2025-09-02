

from rest_framework import serializers
from .models import Listing, Booking, Review




class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {'price_per_night': {'min_value': 0}}
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Listing.objects.all(),
                fields=['title', 'location'],
                message="A listing with this title and location already exists."
            )
        ]
        


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
    def validate(self, data):
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        if data['rating'] < 1 or data['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data
        self.stdout.write(self.style.SUCCESS("Successfully seeded listings!"))