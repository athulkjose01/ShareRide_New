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
        ('Audi A8 L', 'Audi A8 L'),
        ('Audi Q3', 'Audi Q3'),
        ('BMW 3 Series', 'BMW 3 Series'),
        ('BMW X1', 'BMW X1'),
        ('BMW X5', 'BMW X5'),
        ('BYD Atto 3', 'BYD Atto 3'),
        ('Ferrari Roma', 'Ferrari Roma'),
        ('Fiat 500', 'Fiat 500'),
        ('Fiat Abarth Punto', 'Fiat Abarth Punto'),
        ('Fiat Avventura', 'Fiat Avventura'),
        ('Fiat Linea', 'Fiat Linea'),
        ('Fiat Punto', 'Fiat Punto'),
        ('Fiat Urban Cross', 'Fiat Urban Cross'),
        ('Ford EcoSport', 'Ford EcoSport'),
        ('Honda Amaze', 'Honda Amaze'),
        ('Honda BR-V', 'Honda BR-V'),
        ('Honda Civic', 'Honda Civic'),
        ('Honda City', 'Honda City'),
        ('Honda WR-V', 'Honda WR-V'),
        ('Hyundai Alcazar', 'Hyundai Alcazar'),
        ('Hyundai Creta', 'Hyundai Creta'),
        ('Hyundai Exter', 'Hyundai Exter'),
        ('Hyundai Grand i10 Nios', 'Hyundai Grand i10 Nios'),
        ('Hyundai Ioniq 5', 'Hyundai Ioniq 5'),
        ('Hyundai Kona Electric', 'Hyundai Kona Electric'),
        ('Hyundai Tucson', 'Hyundai Tucson'),
        ('Hyundai Venue', 'Hyundai Venue'),
        ('Hyundai Verna', 'Hyundai Verna'),
        ('Jaguar F-Pace', 'Jaguar F-Pace'),
        ('Jeep Compass', 'Jeep Compass'),
        ('Jeep Grand Cherokee', 'Jeep Grand Cherokee'),
        ('Kia Carens', 'Kia Carens'),
        ('Kia Carnival', 'Kia Carnival'),
        ('Kia EV6', 'Kia EV6'),
        ('Kia Seltos', 'Kia Seltos'),
        ('Kia Sonet', 'Kia Sonet'),
        ('Kia Sportage', 'Kia Sportage'),
        ('Lamborghini Urus', 'Lamborghini Urus'),
        ('Land Rover Defender', 'Land Rover Defender'),
        ('Land Rover Discovery Sport', 'Land Rover Discovery Sport'),
        ('Lexus RX 500h', 'Lexus RX 500h'),
        ('Mahindra Bolero', 'Mahindra Bolero'),
        ('Mahindra Marazzo', 'Mahindra Marazzo'),
        ('Mahindra Scorpio', 'Mahindra Scorpio'),
        ('Mahindra Thar', 'Mahindra Thar'),
        ('Mahindra XUV300', 'Mahindra XUV300'),
        ('Mahindra XUV400 EV', 'Mahindra XUV400 EV'),
        ('Mahindra XUV700', 'Mahindra XUV700'),
        ('Maruti Suzuki Alto', 'Maruti Suzuki Alto'),
        ('Maruti Suzuki Baleno', 'Maruti Suzuki Baleno'),
        ('Maruti Suzuki Brezza', 'Maruti Suzuki Brezza'),
        ('Maruti Suzuki Ciaz', 'Maruti Suzuki Ciaz'),
        ('Maruti Suzuki Dzire', 'Maruti Suzuki Dzire'),
        ('Maruti Suzuki Eeco', 'Maruti Suzuki Eeco'),
        ('Maruti Suzuki Fronx', 'Maruti Suzuki Fronx'),
        ('Maruti Suzuki Grand Vitara', 'Maruti Suzuki Grand Vitara'),
        ('Maruti Suzuki Ignis', 'Maruti Suzuki Ignis'),
        ('Maruti Suzuki Maruti 800', 'Maruti Suzuki Maruti 800'),
        ('Maruti Suzuki Swift', 'Maruti Suzuki Swift'),
        ('Maruti Suzuki Wagon R', 'Maruti Suzuki Wagon R'),
        ('Mercedes-Benz C-Class', 'Mercedes-Benz C-Class'),
        ('Mercedes-Benz E-Class', 'Mercedes-Benz E-Class'),
        ('Mercedes-Benz G-Class', 'Mercedes-Benz G-Class'),
        ('Mercedes-Benz GLS', 'Mercedes-Benz GLS'),
        ('MG Hector', 'MG Hector'),
        ('MG ZS EV', 'MG ZS EV'),
        ('Mini Cooper SE', 'Mini Cooper SE'),
        ('Mitsubishi Pajero Sport', 'Mitsubishi Pajero Sport'),
        ('Nissan Compact MPV', 'Nissan Compact MPV'),
        ('Nissan Compact SUV', 'Nissan Compact SUV'),
        ('Nissan GT-R', 'Nissan GT-R'),
        ('Nissan Kicks', 'Nissan Kicks'),
        ('Nissan Leaf', 'Nissan Leaf'),
        ('Nissan Magnite', 'Nissan Magnite'),
        ('Nissan Micra', 'Nissan Micra'),
        ('Nissan Patrol', 'Nissan Patrol'),
        ('Nissan Sunny', 'Nissan Sunny'),
        ('Nissan Terra', 'Nissan Terra'),
        ('Nissan Terrano', 'Nissan Terrano'),
        ('Nissan X-Trail', 'Nissan X-Trail'),
        ('Porsche Macan', 'Porsche Macan'),
        ('Renault Kiger', 'Renault Kiger'),
        ('Renault Kwid', 'Renault Kwid'),
        ('Renault Triber', 'Renault Triber'),
        ('Rolls-Royce Ghost', 'Rolls-Royce Ghost'),
        ('Skoda Kushaq', 'Skoda Kushaq'),
        ('Skoda Octavia', 'Skoda Octavia'),
        ('Skoda Slavia', 'Skoda Slavia'),
        ('Skoda Superb', 'Skoda Superb'),
        ('Tata Altroz', 'Tata Altroz'),
        ('Tata Harrier', 'Tata Harrier'),
        ('Tata Hexa', 'Tata Hexa'),
        ('Tata Nexon', 'Tata Nexon'),
        ('Tata Nexon EV', 'Tata Nexon EV'),
        ('Tata Punch', 'Tata Punch'),
        ('Tata Safari', 'Tata Safari'),
        ('Tata Tigor EV', 'Tata Tigor EV'),
        ('Tata Tiago', 'Tata Tiago'),
        ('Toyota Camry', 'Toyota Camry'),
        ('Toyota Corolla Altis', 'Toyota Corolla Altis'),
        ('Toyota Fortuner', 'Toyota Fortuner'),
        ('Toyota Hilux', 'Toyota Hilux'),
        ('Toyota Innova Crysta', 'Toyota Innova Crysta'),
        ('Toyota Urban Cruiser Hyryder', 'Toyota Urban Cruiser Hyryder'),
        ('Toyota Vellfire', 'Toyota Vellfire'),
        ('Volkswagen Polo', 'Volkswagen Polo'),
        ('Volkswagen Taigun', 'Volkswagen Taigun'),
        ('Volkswagen Tiguan', 'Volkswagen Tiguan'),
        ('Volkswagen Virtus', 'Volkswagen Virtus'),
        ('Volvo XC40', 'Volvo XC40'),
    ]


    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('ev', 'EV'),
        ('hybrid', 'Hybrid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.CharField(max_length=50, choices=CAR_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='petrol')
    features = models.TextField()
    vehicle_number = models.CharField(max_length=15, default='KL 34A 7617')
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
    seats_offered = models.IntegerField(default=4)


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



class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('from_user', 'ride', 'to_user')

    def __str__(self):
        return f"Rating from {self.from_user.username} to {self.to_user.username} for ride {self.ride.id}"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_banned = models.BooleanField(default=False)
    banned_email = models.EmailField(blank=True, null=True)
    banned_mobile = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default.png')

    def __str__(self):
        return self.user.username

    @property
    def report_count(self):
        return UserReport.objects.filter(reported_user=self.user).count()

    def average_rating(self):
        ratings = Rating.objects.filter(to_user=self.user)
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0.0

    def ban_user(self):
        self.is_banned = True
        self.banned_email = self.user.email
        self.banned_mobile = self.mobile_number
        self.save()
        self.user.is_active = False
        self.user.save()
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
    



class UserReport(models.Model):
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reporting_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ride = models.ForeignKey('Ride', on_delete=models.CASCADE)
    
    class Meta:
        # Ensure a user can only report another user once per ride
        unique_together = ('reporting_user', 'reported_user', 'ride')
    



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)  # Single tick
    delivered = models.BooleanField(default=False)  # First Blue Tick
    read = models.BooleanField(default=False) # Second Blue Tick

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']  # Order messages by time




class RideRequestTemporary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride_date = models.DateField()
    ride_time = models.TimeField()
    start_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    polyline = models.TextField()  # Store the encoded polyline
    distance = models.FloatField(null=True, blank=True)  # Distance in kilometers or miles

    created_at = models.DateTimeField(auto_now_add=True)  # Add creation timestamp

    def __str__(self):
        return f"Ride Request by {self.user.username} on {self.ride_date} at {self.ride_time}"



    



    


