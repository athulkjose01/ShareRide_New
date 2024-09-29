from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib import admin
from decimal import Decimal



class RideGiver(models.Model):
    CAR_CHOICES = [
        ('Alto', 'Alto'),
        ('Wagon R', 'Wagon R'),
        ('Swift', 'Swift'),
        ('Dzire', 'Dzire'),
        ('Baleno', 'Baleno'),
        ('Brezza', 'Brezza'),
        ('Grand Vitara', 'Grand Vitara'),
        ('Ciaz', 'Ciaz'),
        ('XL6', 'XL6'),
        ('Eeco', 'Eeco'),
        ('Grand i10 Nios', 'Grand i10 Nios'),
        ('i20', 'i20'),
        ('Creta', 'Creta'),
        ('Venue', 'Venue'),
        ('Verna', 'Verna'),
        ('Alcazar', 'Alcazar'),
        ('Kona Electric', 'Kona Electric'),
        ('Seltos', 'Seltos'),
        ('Carens', 'Carens'),
        ('Sonet', 'Sonet'),
        ('EV6', 'EV6'),
        ('Nexon', 'Nexon'),
        ('Innova', 'Innova'),
        ('Punch', 'Punch'),
        ('Tiago', 'Tiago'),
        ('Harrier', 'Harrier'),
        ('Safari', 'Safari'),
        ('Nexon EV', 'Nexon EV'),
        ('Scorpio', 'Scorpio'),
        ('Thar', 'Thar'),
        ('XUV700', 'XUV700'),
        ('Bolero', 'Bolero'),
        ('XUV300', 'XUV300'),
        ('Fortuner', 'Fortuner'),
        ('Innova Crysta', 'Innova Crysta'),
        ('Camry', 'Camry'),
        ('Corolla Altis', 'Corolla Altis'),
        ('City', 'City'),
        ('Amaze', 'Amaze'),
        ('WR-V', 'WR-V'),
        ('Civic', 'Civic'),
        ('Magnite', 'Magnite'),
        ('Kicks', 'Kicks'),
        ('Kushaq', 'Kushaq'),
        ('Slavia', 'Slavia'),
        ('Octavia', 'Octavia'),
        ('Taigun', 'Taigun'),
        ('Polo', 'Polo'),
        ('C-Class', 'C-Class'),
        ('E-Class', 'E-Class'),
        ('3 Series', '3 Series'),
    ]

    FUEL_TYPE_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.CharField(max_length=50, choices=CAR_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='Petrol')
    features = models.TextField()
    mobile_number = models.CharField(max_length=15, null=True)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user'], name='unique_ridegiver_user')
        ]

    def __str__(self):
        return f"{self.user.username}"



class Ride(models.Model):
    ride_giver = models.ForeignKey(RideGiver, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    polyline = models.TextField(null=True)
    ride_date = models.DateField(default=timezone.now)
    ride_time = models.TimeField(default=timezone.now)
    car_model = models.CharField(max_length=50)

    def clean(self):
        current_date = timezone.now().date()
        current_time = timezone.now().time()

        # If the ride date is today and ride time is in the past, raise a validation error
        if self.ride_date == current_date and self.ride_time < current_time:
            raise ValidationError("Ride time cannot be earlier than the current time for today's date.")

    def save(self, *args, **kwargs):
        # Validate before saving
        self.clean()  # Call the clean method to validate the date and time

        if not self.car_model:
            self.car_model = self.ride_giver.car

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Ride by {self.ride_giver.user.username} on {self.ride_date} at {self.ride_time}"


from decimal import Decimal

class RideRequest(models.Model):

    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    JOINED = 'joined'
    COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (REQUESTED, 'Requested'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (JOINED, 'Joined'),
        (COMPLETED, 'Completed'),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride_date = models.DateField(default=timezone.now)
    ride_time = models.TimeField(default=timezone.now)
    start_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    polyline = models.TextField(null=True)
    distance = models.FloatField(default=0.0)  # New field for distance in kilometers
    ride_giver_start = models.CharField(max_length=255)
    ride_giver_destination = models.CharField(max_length=255)
    car_model = models.CharField(max_length=50, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=REQUESTED,
    )

    def save(self, *args, **kwargs):
        # Check if the status is changing to 'completed'
        if self.pk:
            old_request = RideRequest.objects.get(pk=self.pk)
            if old_request.status != 'completed' and self.status == 'completed':
                # Update the RideGiver's account_balance when RideRequest is marked as 'completed'
                ride_giver = self.ride.ride_giver
                if self.cost:  # Ensure cost is available
                    # Multiply 0.9 (float) by cost (Decimal) by converting 0.9 to Decimal
                    ride_giver.account_balance += (Decimal('0.9') * self.cost)  # Add 90% of the cost
                    ride_giver.save()  # Save the updated balance

        # Ensure car_model is set before saving
        self.car_model = self.ride.ride_giver.car
        super().save(*args, **kwargs)







class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Signal to automatically create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Signal to automatically save the UserProfile whenever the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()




class JoinedRide(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('completed', 'Completed'),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    request = models.ForeignKey(RideRequest, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')

    def __str__(self):
        return f'Ride: {self.ride.id}, Request: {self.request.id}, Status: {self.status}'
    

    



    


