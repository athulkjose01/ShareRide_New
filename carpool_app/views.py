import datetime
from django.utils import timezone
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os
import re
from django.db import models
from django.core import serializers
from django.views import View
import googlemaps
from django.db.models import F
from .forms import RideForm, RideGiverForm, RideCreateForm
from django.views.decorators.http import require_POST
import polyline as polyline_decode
from geopy.distance import geodesic
from googlemaps.convert import decode_polyline
from math import radians, sin, cos, sqrt, atan2
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone 
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from collections import defaultdict
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .forms import PasswordResetForm
from .forms import CustomSetPasswordForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import JoinedRide, Rating, Ride, RideRequest, RideRequestTemporary, UserProfile, UserReport, Message
import json
from datetime import datetime
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import RideGiver
from .forms import RideGiverForm
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
import pickle
import numpy as np
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .models import UserProfile
from twilio.rest import Client
from django.utils.timezone import now
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




class LoginView(View):
    template_name = 'rides/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Ensure the user has a UserProfile
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
            
            if user.is_superuser and user.username == 'shareride':
                # Log in the superuser
                login(request, user)
                # Redirect to the Admin Dashboard with a next parameter
                return redirect("admin_dashboard") 
            else:
                login(request, user)
                return redirect("home")
        else:
            error_message = "Incorrect username or password!"
            return render(request, self.template_name, {'error_message': error_message})
        



def register(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        mobile_number = request.POST['mobile_number']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Password confirmation check
        if password != confirm_password:
            error_message = "Password don't match."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Password length check
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Password complexity check
        if not any(char.isupper() for char in password) or \
           not any(char.islower() for char in password) or \
           not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]|\\~" for char in password):
            error_message = "Password must contain at least one uppercase letter, one lowercase letter, and one special character."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = "This username is already taken. Please choose a different one."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Check if mobile number is banned or already exists
        if UserProfile.objects.filter(mobile_number=mobile_number).exists() or \
           UserProfile.objects.filter(banned_mobile=mobile_number).exists():
            error_message = "This mobile number cannot be used. Please use a different one."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Check if email is banned or already exists
        if User.objects.filter(email=email).exists() or \
           UserProfile.objects.filter(banned_email=email).exists():
            error_message = "This email cannot be used. Please use a different one."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Email format check using regular expressions
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message = "Invalid email format. Please enter a valid email address."
            return render(request, 'rides/register.html', {'error_message': error_message})

        try:
            # Create the user and save it
            myuser = User.objects.create_user(username=username, email=email, password=password)
            myuser.first_name = name
            myuser.save()

            # Update the UserProfile mobile_number (profile is already created via the signal)
            user_profile = UserProfile.objects.get(user=myuser)
            user_profile.mobile_number = mobile_number
            user_profile.save()

            return redirect('login')

        except Exception as e:
            error_message = "An error occurred during registration. Please try again."
            return render(request, 'rides/register.html', {'error_message': error_message})

    return render(request, 'rides/register.html')


class LogoutView(LogoutView):
    next_page = 'match_rides' 





def home(request):
    form = RideForm()
    sos_visible = False
    notification_count = 0  # Initialize notification count

    # Get today's date and tomorrow's date
    today = datetime.now().date()
    tomorrow = today + timedelta(days=-1)  # Corrected line

    if request.user.is_authenticated:
        # For ride takers, check if there is a ride request with 'joined' status
        ride_request_exists = RideRequest.objects.filter(
            user=request.user,
            status='joined',
            ride_date__in=[today, tomorrow]
        ).exists()

        # Check if the user is a RideGiver
        try:
            ride_giver = RideGiver.objects.get(user=request.user)
            ride_requests = RideRequest.objects.filter(ride__ride_giver=ride_giver, ride_date__in=[today, tomorrow])

            # Check if any user has 'joined' status in their ride request
            ride_request_exists_for_giver = ride_requests.filter(status='joined').exists()

            # If any ride request has 'joined' status, show SOS
            sos_visible = ride_request_exists_for_giver

            # Calculate notification count for ride giver
            # Count pending ride requests for rides given by this user
            notification_count += RideRequest.objects.filter(
                ride__ride_giver=ride_giver,
                status='requested', #checking for any pendin reques
                ride__ride_date__gte=today
            ).count()



        except RideGiver.DoesNotExist:
            ride_request_exists_for_giver = False

        # Combine conditions: show SOS if any ride request for the user or ride giver has 'joined' status
        sos_visible = sos_visible or ride_request_exists

        # Calculate notification count for ride taker
        # Count accepted ride requests that the user has made
        notification_count += RideRequest.objects.filter(
            user=request.user,
            status='accepted', # checkign for any accept request to show in the navbar
            ride__ride_date__gte=today
        ).count()
        # also check for the requested ride to show count in the navbar, it means ride giver requested his ride,
        notification_count += RideRequest.objects.filter(
            user=request.user,
            status='requested',  # Assuming 'requested' is the status for pending requests
            ride__ride_date__gte=today
        ).count()

    return render(request, 'rides/ride_taker.html', {'form': form, 'sos_visible': sos_visible, 'notification_count': notification_count})



def ride_request(request):  # Renamed for clarity
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)

            start_location = json_data.get('start')
            destination = json_data.get('destination')
            ride_date_str = json_data.get('date')  # Date is coming as a string
            ride_time_str = json_data.get('time')   # Time is coming as a string
            polyline = json_data.get('polyline')

            # Convert date and time strings to Python objects
            ride_date = datetime.strptime(ride_date_str, '%Y-%m-%d').date()
            ride_time = datetime.strptime(ride_time_str, '%H:%M').time()

            # You might want to calculate distance here using the polyline,
            # Google Maps API, or other methods.  Leaving it as None for now.
            distance = None

            # Create the RideRequestTemporary object
            ride_request_temp = RideRequestTemporary(
                user=request.user,
                ride_date=ride_date,
                ride_time=ride_time,
                start_location=start_location,
                destination=destination,
                polyline=polyline,
                distance=distance
            )
            ride_request_temp.save()

            # You can render a template or return a JSON response.  This is just an example.
            return render(request, 'rides/match_rides_results.html', {'message': 'Ride request saved!'})


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)  # Return error message

    else:
        return HttpResponse("Invalid request.", status=400)

import json




@login_required
def save_route(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start = data.get('start')
        destination = data.get('destination')
        polyline = data.get('polyline')
        date = data.get('ride_date')
        time = data.get('ride_time')
        seats_offered = data.get('seats_offered', 4)  # Get seats_offered from request

        try:
            ride_giver = RideGiver.objects.get(user=request.user)
        except RideGiver.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'RideGiver not found for the current user'})

        Ride.objects.create(
            ride_giver=ride_giver,
            start_location=start,
            destination=destination,
            polyline=polyline,
            ride_date=date,
            ride_time=time,
            car_model=ride_giver.car,
            seats_offered=seats_offered  # Add seats_offered
        )

        return JsonResponse({'status': 'success', 'redirect_url': '/ride-created/'})

    return JsonResponse({'status': 'fail'})




def ride_created(request):
    return render(request, 'rides/ride_created.html')






def show_polyline(request):
    rides = Ride.objects.all()
    return render(request, 'rides/show_polyline.html', {'rides': rides})



def get_coordinates(request):
    ride_id = request.GET.get('ride')
    ride = Ride.objects.get(pk=ride_id)
    polyline = ride.polyline

    gmaps = googlemaps.Client(key='AIzaSyBnX3vMyrAvLILwOvs7c8P9soMWP7D3TEI')  # Replace with your Google Maps API key

    decoded_polyline = googlemaps.convert.decode_polyline(polyline)

    coordinates = []
    for point in decoded_polyline:
        lat = round(point['lat'], 2)  # Round latitude to 3 decimal places
        lng = round(point['lng'], 2)  # Round longitude to 3 decimal places
        coordinates.append({
            'lat': lat,
            'lng': lng,
        })

    return render(request, 'rides/show_polyline.html', {'rides': Ride.objects.all(), 'coordinates': coordinates})



class GiveRidesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            ride_giver = RideGiver.objects.get(user=request.user)
            form = RideCreateForm()
            return render(request, 'rides/home.html', {'form': form})
        except RideGiver.DoesNotExist:
            message = "Please add your car details first."
            return render(request, 'rides/ride_giver_prompt.html', {'message': message})




def save_request_route(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start = data['start']
        destination = data['destination']
        polyline = data['polyline']
        ride_id = data.get('ride_id')

        ride = Ride.objects.get(id=ride_id)
        RideRequest.objects.create(
            ride=ride,
            user=request.user,  # Automatically assign the current user as the requester
            start_location=start,
            destination=destination,
            polyline=polyline,
            ride_date=ride.ride_date,  # Set ride date
            ride_time=ride.ride_time,  # Set ride time
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})



def show_request_polyline(request):
    rides = RideRequest.objects.all()
    return render(request, 'rides/show_requestpolyline.html', {'rides': rides})




def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return 6371 * c

def compute_polyline_distance(points):
    """
    Calculate the total distance of a polyline.
    """
    total_distance = 0
    for i in range(len(points) - 1):
        total_distance += haversine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    return total_distance

def decode_polyline(polyline):
    """
    Decode a polyline string into a list of latitude/longitude points.
    """
    points = []
    index = 0
    lat = 0
    lng = 0
    while index < len(polyline):
        b = 0
        shift = 0
        result = 0
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat
        shift = 0
        result = 0
        while True:
            b = ord(polyline[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        points.append({'lat': lat * 1e-5, 'lng': lng * 1e-5})
    return points

def get_place_name(lat, lng):
    """
    Get the real place name from latitude and longitude using Google Maps Geocoding API.
    Removes Plus Codes from the address.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                full_address = data['results'][0]['formatted_address']
                parts = full_address.split(',', 1)
                if len(parts) > 1:
                  return parts[1].strip()
                else:
                  return full_address.strip()
        return f"{lat:.5f}, {lng:.5f}"
    except Exception:
      return f"{lat:.5f}, {lng:.5f}"


def match_rides(request):
    data = json.loads(request.body)
    start = data['start']
    destination = data['destination']
    polyline = data['polyline']
    date = data['date']
    time = data['time']

    decoded_taker_polyline = decode_polyline(polyline)
    taker_points = [(point['lat'], point['lng']) for point in decoded_taker_polyline]
    taker_total_distance = compute_polyline_distance(taker_points)
    taker_start = taker_points[0]
    taker_end = taker_points[-1]

    # Convert ride taker's requested time to datetime
    taker_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key='AIzaSyBnX3vMyrAvLILwOvs7c8P9soMWP7D3TEI')
    
    matched_rides = []
    today = datetime.now().date()
    now_time = datetime.now().time()

    ride_queryset = Ride.objects.filter(
        ride_date=date
    ).annotate(
        joined_count=Count('joinedride'),
        num_passengers=Count('joinedride')
    ).filter(num_passengers__lt=models.F('seats_offered'))

    if date == str(today):
        ride_queryset = ride_queryset.filter(Q(ride_time__gte=now_time))

    for ride in ride_queryset:
        ride_decoded_polyline = decode_polyline(ride.polyline)
        giver_points = [(point['lat'], point['lng']) for point in ride_decoded_polyline]

        pickup_distances = [haversine(taker_start[0], taker_start[1], p[0], p[1]) for p in giver_points]
        pickup_index = pickup_distances.index(min(pickup_distances))
        
        dropoff_distances = [haversine(taker_end[0], taker_end[1], p[0], p[1]) for p in giver_points]
        dropoff_index = dropoff_distances.index(min(dropoff_distances))
    
        if pickup_index > dropoff_index:
            continue

        # Calculate travel time from ride giver's start to rider's pickup point
        ride_start_location = f"{giver_points[0][0]},{giver_points[0][1]}"
        pickup_location = f"{taker_start[0]},{taker_start[1]}"
        
        try:
            directions_result = gmaps.directions(
                ride_start_location,
                pickup_location,
                mode="driving",
                departure_time=datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), 
                                             datetime.strptime(str(ride.ride_time), '%H:%M:%S').time())
            )
            
            if directions_result:
                # Get duration in seconds and convert to minutes
                duration_to_pickup = directions_result[0]['legs'][0]['duration']['value'] / 60
                
                # Calculate estimated pickup time
                ride_start_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), 
                                                     ride.ride_time)
                estimated_pickup_time = ride_start_datetime + timedelta(minutes=duration_to_pickup)
                
                # Check if pickup time is within 2 hours before or after requested time
                time_difference = abs((estimated_pickup_time - taker_datetime).total_seconds() / 3600)
                
                if time_difference > 1:
                    continue
                
            else:
                continue
                
        except Exception as e:
            print(f"Error calculating directions: {e}")
            continue

        giver_segment = giver_points[pickup_index:dropoff_index+1]
        overlapping_distance = compute_polyline_distance(giver_segment)
        match_percent = min((overlapping_distance / taker_total_distance) * 100, 100)
        is_100_percent = match_percent >= 96.5

        if not is_100_percent:
            taker_rounded = set((round(p[0], 5), round(p[1], 5)) for p in taker_points)
            common_indices = []
            for idx, p in enumerate(giver_points):
                if (round(p[0], 5), round(p[1], 5)) in taker_rounded:
                    common_indices.append(idx)
            
            if common_indices:
                new_pickup_index = common_indices[0]
                new_dropoff_index = common_indices[-1]
                
                if new_pickup_index > new_dropoff_index:
                    new_pickup_index, new_dropoff_index = new_dropoff_index, new_pickup_index
                
                new_giver_segment = giver_points[new_pickup_index:new_dropoff_index+1]
                new_overlapping = compute_polyline_distance(new_giver_segment)
                new_match_percent = (new_overlapping / taker_total_distance) * 100
                
                if new_match_percent >= 60:
                    pickup_index = new_pickup_index
                    dropoff_index = new_dropoff_index
                    overlapping_distance = new_overlapping
                    match_percent = new_match_percent

        pickup_point = giver_points[pickup_index]
        dropoff_point = giver_points[dropoff_index]
        
        pickup_name = get_place_name(pickup_point[0], pickup_point[1])
        dropoff_name = get_place_name(dropoff_point[0], dropoff_point[1])

        distance_to_pickup = haversine(taker_start[0], taker_start[1], pickup_point[0], pickup_point[1])
        distance_from_dropoff = haversine(dropoff_point[0], dropoff_point[1], taker_end[0], taker_end[1])

        if match_percent >= 60:
            travel_companions = JoinedRide.objects.filter(ride=ride).select_related('request__user__userprofile')
            companions_data = []
            for companion in travel_companions:
                companions_data.append({
                    'user_id': companion.request.user.id if companion.request and companion.request.user else None,
                    'username': companion.request.user.username if companion.request and companion.request.user else 'Unknown',
                    'profile_picture': companion.request.user.userprofile.profile_picture.url if companion.request and companion.request.user and companion.request.user.userprofile.profile_picture else None,
                })

            if distance_to_pickup <= 4.0 and distance_from_dropoff <= 4.0:
                is_100_percent = True
                match_percent = 100

            matched_rides.append({
                'ride_giver_start': ride.start_location,
                'ride_taker_start': start,
                'ride_taker_destination': destination,
                'ride_giver_destination': ride.destination,
                'ride': ride,
                'date': date,
                'time': time,
                'distance': taker_total_distance,
                'polyline': polyline,
                'companions': companions_data,
                'match_percent': round(match_percent),
                'is_100_percent': is_100_percent,
                'pickup_name': pickup_name,
                'dropoff_name': dropoff_name,
                'overlap_distance': overlapping_distance,
                'taker_total_distance': taker_total_distance,
                'distance_to_pickup': distance_to_pickup + 2.0,
                'distance_from_dropoff': distance_from_dropoff + 2.0,
                'estimated_pickup_time': estimated_pickup_time.strftime('%I:%M %p'),
            })

    matched_rides.sort(key=lambda x: x['match_percent'], reverse=True)

    return render(request, 'rides/ride_taker_results.html', {
        'matched_rides': matched_rides
    })


def load_model_and_encoders():
    # Directory where views.py (and app directory) is located
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to the models and encoders
    model_path = os.path.join(app_dir, 'ml_models', 'random_forest_model.pkl')
    label_encoder_model_path = os.path.join(app_dir, 'ml_models', 'label_encoder_model.pkl')
    label_encoder_fuel_path = os.path.join(app_dir, 'ml_models', 'label_encoder_fuel.pkl')

    # Load Random Forest model
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    # Load Label Encoder for model
    with open(label_encoder_model_path, 'rb') as file:
        label_encoder_model = pickle.load(file)

    # Load Label Encoder for fuel
    with open(label_encoder_fuel_path, 'rb') as file:
        label_encoder_fuel = pickle.load(file)

    return model, label_encoder_model, label_encoder_fuel


model, label_encoder_model, label_encoder_fuel = load_model_and_encoders()


CAR_RATINGS = {
    'Maruti Suzuki Alto': 6,
    'Maruti Suzuki Wagon R': 7,
    'Maruti Suzuki Swift': 8,
    'Maruti Suzuki Dzire': 8,
    'Maruti Suzuki Baleno': 9,
    'Maruti Suzuki Brezza': 10,
    'Maruti Suzuki Grand Vitara': 11,
    'Maruti Suzuki Ciaz': 11,
    'Maruti Suzuki XL6': 10,
    'Maruti Suzuki Eeco': 5,
    'Maruti Suzuki Fronx': 9,
    'Maruti Suzuki Maruti 800': 5,
    'Maruti Suzuki Ignis': 6,
    'Hyundai Grand i10 Nios': 8,
    'Hyundai i20': 9,
    'Hyundai Creta': 11,
    'Hyundai Venue': 10,
    'Hyundai Verna': 11,
    'Hyundai Alcazar': 12,
    'Hyundai Kona Electric': 14,
    'Hyundai Exter': 9,
    'Hyundai Tucson': 12,
    'Hyundai Ioniq 5': 15,
    'Kia Seltos': 11,
    'Kia Carens': 12,
    'Kia Sonet': 10,
    'Kia EV6': 15,
    'Kia Carnival': 14,
    'Kia Sportage': 13,
    'Tata Nexon': 10,
    'Tata Punch': 9,
    'Tata Tiago': 8,
    'Tata Harrier': 12,
    'Tata Safari': 12,
    'Tata Nexon EV': 14,
    'Tata Altroz': 9,
    'Tata Tigor EV': 13,
    'Tata Hexa': 11,
    'Mahindra Scorpio': 12,
    'Mahindra Thar': 11,
    'Mahindra XUV700': 13,
    'Mahindra Bolero': 9,
    'Mahindra XUV300': 10,
    'Mahindra XUV400 EV': 14,
    'Mahindra Marazzo': 10,
    'Toyota Fortuner': 13,
    'Toyota Innova Crysta': 12,
    'Toyota Camry': 14,
    'Toyota Corolla Altis': 11,
    'Toyota Hilux': 13,
    'Toyota Vellfire': 14,
    'Toyota Urban Cruiser Hyryder': 11,
    'Honda City': 10,
    'Honda Amaze': 9,
    'Honda WR-V': 10,
    'Honda Civic': 12,
    'Honda BR-V': 10,
    'Renault Kwid': 6,
    'Renault Triber': 8,
    'Renault Kiger': 9,
    'Skoda Kushaq': 11,
    'Skoda Slavia': 11,
    'Skoda Octavia': 12,
    'Skoda Superb': 14,
    'Volkswagen Taigun': 11,
    'Volkswagen Polo': 9,
    'Volkswagen Tiguan': 12,
    'Volkswagen Virtus': 11,
    'Mercedes-Benz C-Class': 13,
    'Mercedes-Benz E-Class': 15,
    'Mercedes-Benz GLS': 15,
    'Mercedes-Benz G-Class': 16,
    'BMW 3 Series': 13,
    'BMW X1': 13,
    'BMW X5': 15,
    'Audi Q3': 13,
    'Audi A8 L': 15,
    'Volvo XC40': 13,
    'Jaguar F-Pace': 14,
    'Land Rover Discovery Sport': 15,
    'Land Rover Defender': 16,
    'Jeep Compass': 12,
    'Jeep Grand Cherokee': 15,
     'Lexus RX 500h': 15,
    'Porsche Macan': 16,
    'Ferrari Roma': 16,
    'Lamborghini Urus': 16,
    'Rolls-Royce Ghost': 16,
     'Nissan Magnite': 9,
    'Nissan Terrano': 10,
    'MG Hector': 12,
    'MG ZS EV': 14,
    'BYD Atto 3': 14,
    'Mini Cooper SE': 14,
    'Mitsubishi Pajero Sport': 12,
    'Isuzu D-Max V-Cross': 13,
     'Fiat Punto': 7,
    'Fiat Linea': 8,
    'Fiat Abarth Punto': 8,
    'Fiat Urban Cross': 8,
    'Fiat Avventura': 8,
    'Fiat 500': 9,
     'Ford EcoSport': 9,
     'Maruti Suzuki Defender': 16,
     'Nissan Micra':	7,
      'Nissan Sunny':	8,
      'Nissan Kicks':	9,
      'Nissan GT-R':	16,
       'Nissan X-Trail':	13,
       'Nissan Leaf':	12,
      'Nissan Patrol':	14,
      'Nissan Terra':	11,
       'Nissan Compact MPV':	8,
      'Nissan Compact SUV':	10,
     'Hyundai Getz': 6
}

@csrf_exempt
def predict_cost(request):
    if request.method == 'POST':
        distance = float(request.POST.get('distance'))
        car_model = request.POST.get('car_model')
        fuel_type = request.POST.get('fuel_type')

        if car_model not in CAR_RATINGS:
             return JsonResponse({'error': 'Invalid car model'}, status=400)

        rating = CAR_RATINGS.get(car_model)
        base_cost = distance * (rating / 3.0)
        
        if fuel_type == 'diesel':
              cost = base_cost * Decimal('0.95')
        elif fuel_type == 'ev':
             cost = base_cost * Decimal('0.90')
        elif fuel_type == 'hybrid':
            cost = base_cost * Decimal('0.92')
        else: # petrol
            cost = base_cost
        
        return JsonResponse({'predicted_cost': float(cost)})

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@login_required
def request_ride(request):
    if request.method == 'POST':
        
        start_location = request.POST.get('start_location')
        destination = request.POST.get('destination')
        ride_giver_start = request.POST.get('ride_giver_start')
        ride_giver_destination = request.POST.get('ride_giver_destination')
        polyline = request.POST.get('polyline')
        date = request.POST.get('date')
        time = request.POST.get('time')
        ride_id = request.POST.get('ride_id')
        cost = request.POST.get('cost')

        # Calculate distance using Google Maps API
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        directions_result = gmaps.directions(start_location, destination, mode="driving")

        if directions_result:
            distance = directions_result[0]['legs'][0]['distance']['value'] / 1000  # Convert meters to kilometers
        else:
            distance = 0  # Default to 0 if unable to calculate

        # Fetch the ride by ride_id
        ride = Ride.objects.get(id=ride_id)

        # Create and save the RideRequest
        ride_request = RideRequest.objects.create(
            ride=ride,
            user=request.user,  # Automatically assign the current user as the requester
            ride_date=date,  # Set ride date
            ride_time=time ,
            start_location=start_location,
            destination=destination,
            polyline=polyline,
            distance=distance,
            ride_giver_start=ride_giver_start,
            ride_giver_destination=ride_giver_destination,
            cost = cost
 
        )

        return render(request, 'rides/ride_request_confirmation.html', {'ride_request': ride_request})

    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})







@login_required
def save_ride_giver(request):
    if request.method == 'POST':
        user = request.user  # Get the current logged-in user
        car = request.POST.get('car')
        vehicle_number = request.POST.get('mobile_number')
        fuel_type = request.POST.get('fuel_type')
        features = request.POST.get('features')

        form = RideForm()  # Create a blank form or use this according to your flow

        try:
            # Attempt to create and save RideGiver
            RideGiver.objects.create(user=user, car=car, fuel_type=fuel_type, features=features, vehicle_number=vehicle_number)
            messages.success(request, 'RideGiver details saved successfully!')  # Success message
        except IntegrityError:
            # Handle the case where the user already has a RideGiver entry
            messages.error(request, 'You have already registered as a Ride Giver!')

        return render(request, 'rides/home.html', {'form': form})

    return render(request, 'rides/ride_giver_details.html')



class RideGiverUpdateView(LoginRequiredMixin, UpdateView):
    model = RideGiver
    form_class = RideGiverForm
    template_name = 'rides/update_ride_giver.html'
    success_url = reverse_lazy('give_rides')  # Redirect after successful update

    def get_object(self, queryset=None):
        # Ensure that the logged-in user can only update their own RideGiver entry
        return get_object_or_404(RideGiver, user=self.request.user)
    



@login_required
def view_upcoming_rides(request):
    try:
        ride_giver = RideGiver.objects.get(user=request.user)
    except RideGiver.DoesNotExist:
        ride_giver = None

    today = datetime.now().date()
    now_time = datetime.now().time()
    tomorrow = today + timedelta(days=1)

    # Get user rides with safe queries
    user_rides = Ride.objects.filter(
        Q(ride_giver__user=request.user, ride_date=today, ride_time__gte=now_time) |
        Q(ride_giver__user=request.user, ride_date__gt=today)
    ).order_by('-ride_date', '-ride_time')
    
   # Get all relevant rides
    all_rides = Ride.objects.filter(
        Q(ride_giver__user=request.user) | Q(riderequest__user=request.user)
    ).filter(
        ride_date__gte=today
    ).distinct()

    # Process unique rides safely
    unique_rides = {}
    for ride in all_rides:
        if ride not in unique_rides:
            unique_rides[ride] = {
                'ride_giver': (ride.ride_giver.user, ride.ride_giver.user.username) if ride.ride_giver and ride.ride_giver.user else (None, 'Unknown'),
                'companions': []
            }
        # Get all accepted RideRequests for this ride
        accepted_requests = RideRequest.objects.filter(ride=ride, status= 'joined')
        for request_item in accepted_requests:
           if request_item.user != request.user:
            user = request_item.user
            username = user.username
            unique_rides[ride]['companions'].append((user, username))

    # Get joined rides - Modified to include completed rides for the current and next day
    joined_rides = JoinedRide.objects.select_related(
        'ride__ride_giver__user__userprofile',
        'request__user'
    ).filter(
        request__user=request.user,
        ride__ride_date__in=[today, tomorrow]
    ).order_by('-ride__ride_date', '-ride__ride_time')

    # Get existing reports safely
    existing_reports = UserReport.objects.filter(
        reporting_user=request.user
    ).values_list('reported_user', 'ride')
    reported_rides = set((user_id, ride_id) for user_id, ride_id in existing_reports)

    # Get existing ratings safely
    existing_ratings = Rating.objects.filter(
        from_user=request.user
    ).values_list('to_user', 'ride')
    rated_rides = set((user_id, ride_id) for user_id, ride_id in existing_ratings)

    # Add reporting and rating status safely for the ride taker
    for joined_ride in joined_rides:
        if joined_ride.ride and joined_ride.ride.ride_giver and joined_ride.ride.ride_giver.user:
            reported_tuple = (joined_ride.ride.ride_giver.user.id, joined_ride.ride.id)
            rated_tuple = (joined_ride.ride.ride_giver.user.id, joined_ride.ride.id)
            joined_ride.already_reported = reported_tuple in reported_rides
            joined_ride.already_rated = rated_tuple in rated_rides
        else:
            joined_ride.already_reported = False
            joined_ride.already_rated = False

    # Get requested rides safely - Modified to exclude completed rides
    user_requested_rides = RideRequest.objects.select_related(
        'ride__ride_giver__user__userprofile'
    ).filter(
        user=request.user,
        status__in=['requested', 'accepted']
    ).exclude(
        id__in=JoinedRide.objects.values_list('request_id', flat=True)
    ).filter(
        Q(ride__ride_date=today, ride__ride_time__gte=now_time) |
        Q(ride__ride_date__gt=today)
    ).order_by('ride__ride_date', 'ride__ride_time')

    # Get the list of joined passengers for the ride giver
    if ride_giver:
        ride_giver_joined_rides = JoinedRide.objects.filter(
            ride__ride_giver=ride_giver,
            ride__ride_date__in=[today, tomorrow]
        ).order_by('-ride__ride_date', '-ride__ride_time')

        # Get existing reports and ratings safely for ride giver for the ride taker
        ride_giver_existing_reports = UserReport.objects.filter(
            reporting_user=request.user
        ).values_list('reported_user', 'ride')
        ride_giver_reported_rides = set((user_id, ride_id) for user_id, ride_id in ride_giver_existing_reports)

        ride_giver_existing_ratings = Rating.objects.filter(
            from_user=request.user
        ).values_list('to_user', 'ride')
        ride_giver_rated_rides = set((user_id, ride_id) for user_id, ride_id in ride_giver_existing_ratings)

        for joined in ride_giver_joined_rides:
            if joined.request and joined.request.user and joined.ride:
                ride_giver_reported_tuple = (joined.request.user.id, joined.ride.id)
                ride_giver_rated_tuple = (joined.request.user.id, joined.ride.id)
                joined.already_reported = ride_giver_reported_tuple in ride_giver_reported_rides
                joined.already_rated = ride_giver_rated_tuple in ride_giver_rated_rides
            else:
                joined.already_reported = False
                joined.already_rated = False
    else:
        ride_giver_joined_rides = []

    # Add the list of joined passengers to the context
    context = {
        'user_rides': user_rides,
        'user_requested_rides': user_requested_rides,
        'joined_rides': joined_rides,
        'travel_companions': unique_rides,  # changed the value here
        'unique_rides': unique_rides,
        'today': today,
        'tomorrow': tomorrow,
        'ride_giver_joined_rides': ride_giver_joined_rides,
    }

    return render(request, 'rides/upcoming_rides.html', context)





@login_required
def mark_ride_completed(request, joined_ride_id):
    joined_ride = get_object_or_404(JoinedRide, id=joined_ride_id)
    if request.method == 'POST':
        joined_ride.status = 'completed'
        joined_ride.save()
        messages.success(request, "Ride marked as completed.")
        return redirect('view_upcoming_rides')  # Assuming 'view_upcoming_rides' is the view that displays the rides list
    return render(request, 'rides/mark_ride_completed.html', {'joined_ride': joined_ride})


def accept_request(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride_request.status = 'accepted'
    ride_request.save()
    return redirect('view_upcoming_rides')

def decline_request(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride_request.status = 'declined'
    ride_request.save()
    return redirect('view_upcoming_rides')


@login_required
def join_ride(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id)
    if ride_request.status == 'accepted':
        JoinedRide.objects.get_or_create(
            ride=ride_request.ride,
            request=ride_request,
            status='joined'
        )
        ride_request.status = 'joined'
        ride_request.save()
    return redirect('view_upcoming_rides')


def complete_ride(request, request_id):
    joined_Ride = get_object_or_404(JoinedRide, id=request_id)
    joined_Ride.status = 'Completed'
    joined_Ride.save()
    joined_Ride.request.status = 'completed'
    joined_Ride.request.save()
    return redirect('view_upcoming_rides')



class MyAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'rides/my_account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        viewed_user = user  # Viewing their own profile

        context['is_owner'] = True  # flag for my_account.html
        context['viewed_user'] = viewed_user  # Ensure viewed_user is always in context

        context['report_count'] = user.userprofile.report_count
        context['average_rating'] = user.userprofile.average_rating

        # Joined rides where the current user has joined a ride as a ride taker
        joinedrides = JoinedRide.objects.filter(request__user=user)

        # Rides given by the user (as a ride giver)
        givenrides = Ride.objects.filter(ride_giver__user=user)

        context['user_form'] = CustomUserChangeForm(instance=user)
        context['joinedrides'] = joinedrides
        context['givenrides'] = givenrides


        try:
            ride_giver = RideGiver.objects.get(user=user)
            context['account_balance'] = ride_giver.account_balance
        except RideGiver.DoesNotExist:
            context['account_balance'] = None

        # Calculate rides taken count
        rides_taken_count = RideRequest.objects.filter(user=user).count()
        context['rides_taken_count'] = rides_taken_count

        # Calculate rides created count
        rides_created_count = Ride.objects.filter(ride_giver__user=user).count()
        context['rides_created_count'] = rides_created_count

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'profile_picture' in request.FILES:
            profile_pic = request.FILES['profile_picture']
            userprofile = user.userprofile

            # Check file size
            if profile_pic.size > 5 * 1024 * 1024:  # Limit to 5 MB
                messages.error(request, 'Profile picture size must be 5MB or less.')
                return redirect('my_account')
            
             # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if profile_pic.content_type not in allowed_types:
                messages.error(request, 'Please upload a valid JPEG, PNG, or GIF file.')
                return redirect('my_account')
            userprofile.profile_picture = profile_pic
            userprofile.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('my_account')


        user_form = CustomUserChangeForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your account details have been updated.')
            context = self.get_context_data()
            return render(request, self.template_name, context)
        return render(request, self.template_name, {'user_form': user_form, **self.get_context_data()})

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')



@login_required
def user_profile_view(request, user_id):
    viewed_user = get_object_or_404(User, id=user_id)
    context = {}

    context['is_owner'] = (request.user.id == viewed_user.id)  # check if the user is the owner of the profile
    context['viewed_user'] = viewed_user

    context['report_count'] = viewed_user.userprofile.report_count
    context['average_rating'] = viewed_user.userprofile.average_rating
     
    # Profile picture url
    if hasattr(viewed_user, 'userprofile') and viewed_user.userprofile.profile_picture:
            context['profile_picture_url'] = viewed_user.userprofile.profile_picture.url
    else:
        context['profile_picture_url'] = None


    # Calculate rides taken count for the viewed user
    rides_taken_count = RideRequest.objects.filter(user=viewed_user).count()
    context['rides_taken_count'] = rides_taken_count

    # Calculate rides created count for the viewed user
    rides_created_count = Ride.objects.filter(ride_giver__user=viewed_user).count()
    context['rides_created_count'] = rides_created_count

     # Joined rides where the current user has joined a ride as a ride taker
    joinedrides = JoinedRide.objects.filter(request__user=viewed_user)

    # Rides given by the user (as a ride giver)
    givenrides = Ride.objects.filter(ride_giver__user=viewed_user)

    context['joinedrides'] = joinedrides
    context['givenrides'] = givenrides

    return render(request, 'rides/user_profile.html', context)  # different html file






def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
                send_mail(
                    'Password Reset-SHARE RIDE',
                    f'Click the link to reset your password: {reset_link}',
                    'athul.23pmc116@mariancollege.org',
                    [email],
                    fail_silently=False,
                )
                return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')





UserModel = get_user_model()

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        return HttpResponse('Invalid password reset link.')


def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')




@csrf_exempt
def withdraw_money(request):
    if request.method == "POST":
        user = request.user
        ride_giver = get_object_or_404(RideGiver, user=user)
        
        try:
            amount = Decimal(request.POST.get('amount'))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error_message': 'Invalid amount.'})

        if amount <= 0:
            return JsonResponse({'success': False, 'error_message': 'Amount must be positive.'})

        if amount > ride_giver.account_balance:
            return JsonResponse({'success': False, 'error_message': 'Insufficient balance.'})

        # Update the balance in the RideGiver model
        ride_giver.account_balance -= amount
        ride_giver.save()

        return JsonResponse({'success': True, 'new_balance': float(ride_giver.account_balance)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request.'})




@login_required
def delete_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, ride_giver__user=request.user)
    
    if request.method == 'POST':
        if not ride.joinedride_set.exists():
            # Delete all associated ride requests
            ride.riderequest_set.all().delete()
            # Delete the ride
            ride.delete()
            messages.success(request, "Ride and all associated requests have been successfully deleted.")
        else:
            messages.error(request, "Cannot delete ride with joined passengers.")
    
    return redirect('view_upcoming_rides')






@login_required
def dummy_payment(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id)
    if request.method == 'POST':
        # Process the payment (in this case, just mark it as successful)
        return join_ride(request, request_id)
    return render(request, 'rides/dummy_payment.html', {'ride_request': ride_request})



from groq import Groq

groq_client = Groq(
    api_key=settings.GROQ_API_KEY  # Get the API key from settings.py
)


def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')

        # Get chat history from session
        chat_history = request.session.get('chat_history', [])
        # Add user input to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        
        # Initialize user data string
        user_data_str = ""

        if request.user.is_authenticated:
          user = request.user
          try:
              user_profile = UserProfile.objects.get(user=user)
              mobile_number = user_profile.mobile_number if user_profile.mobile_number else "Not Available"
          except UserProfile.DoesNotExist:
              mobile_number = "Not Available"
          user_data_str += f"User details: username: {user.username}, email: {user.email}, mobile number: {mobile_number}. \n"
            
          try:
              ride_giver = RideGiver.objects.get(user=user)
              user_data_str += f"Ride giver details: car model: {ride_giver.car}, fuel type: {ride_giver.fuel_type}, vehicle number: {ride_giver.vehicle_number}, account balance: {ride_giver.account_balance}. \n"
          except RideGiver.DoesNotExist:
            user_data_str += "Ride giver details: Not registered as a ride giver. \n"

          # Fetch Ride Data for the Current User (as a Ride Giver)
          rides_given = Ride.objects.filter(ride_giver__user=user)
          if rides_given.exists():
              user_data_str += "Rides created by you:\n"
              for ride in rides_given:
                  user_data_str += f"Ride ID: {ride.id}, Car Model: {ride.car_model}, Start location: {ride.start_location}, Destination: {ride.destination}, Ride date: {ride.ride_date}, Ride Time: {ride.ride_time}.\n"
          else:
              user_data_str += "Rides created by you: No rides created yet.\n"
          
          # Fetch Ride Request Data
          ride_requests = RideRequest.objects.filter(user=user)
          if ride_requests.exists():
            user_data_str += "Ride requests made by you:\n"
            for request_obj in ride_requests:
              user_data_str += f"Ride ID: {request_obj.ride.id}, Car Model: {request_obj.car_model}, Ride Giver Start: {request_obj.ride_giver_start}, Ride Giver Destination: {request_obj.ride_giver_destination}, Ride Date: {request_obj.ride_date}, Ride Time: {request_obj.ride_time}, Start location: {request_obj.start_location}, Destination: {request_obj.destination}, Distance: {request_obj.distance} km, Cost: {request_obj.cost}, Status: {request_obj.status}.\n"
          else:
            user_data_str += "Ride requests made by you: No ride requests made yet.\n"

          # Fetch Joined Ride Data
          joined_rides = JoinedRide.objects.filter(request__user=user)
          if joined_rides.exists():
              user_data_str += "Joined Rides with you:\n"
              for joined_ride in joined_rides:
                  user_data_str += f"Joined Ride ID: {joined_ride.id}, Ride ID: {joined_ride.ride.id}, Status: {joined_ride.status}.\n"
          else:
              user_data_str += "Joined Rides with you: No joined rides yet.\n"
        else:
            user_data_str = "User not logged in. Please log in to access personalized data."


        INITIAL_PROMPT = f"""You are a helpful and friendly chatbot specifically designed to assist users with ShareRide, a carpooling app. 
        ShareRide provides online carpool services in Kerala. The app was developed in 2025 by Athul K Jose and headquartered in Kerala, India.
        You should focus on queries related to carpooling, rides, app features, or the company information. 
        If the user asks a general question outside these topics, respond with "I can't answer that." If the user asks for irrelevant questions respond "I cant answer that".
        If the user says hi or hello or introduces themselves, then greet them.
        For the first message, you should respond with "Welcome to ShareRide! How can I help you?". Remember previous interactions.
        give proper next line break after every sentence.
        dont give * in the response.
        
        {user_data_str}
        note that username is same as my name.
        and note that the Ride model is for - ride that is created (by the ride giver)
        RideGiver - RideGiver details
        RideRequest - Ride requested by the passengers(Ride Takers)
        JoinedRide - data related to the both the ride taker and ride giver in a joined ride (give this in prompt(the data is related to what)).
        note that dont provide any ids in reponses like ride id, riderequest id etc. but you can provide email id, username, mobile number, vehicle number etc.
        give these informations if the user asks it only.
        """
        # construct prompt
        messages=[
                {"role": "system", "content": INITIAL_PROMPT},
            ]
        messages.extend(chat_history)
        
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",
            )
            response = chat_completion.choices[0].message.content

            # Add line breaks to the response
            response_with_breaks = response.replace(". ", ".<br>")


            # Add bot's response to chat history
            chat_history.append({"role":"assistant", "content":response_with_breaks})

            # update session with new chat history
            request.session['chat_history'] = chat_history

        except Exception as e:
            response = f"Error during API call: {e}"

        return JsonResponse({'response': response_with_breaks})

    request.session['chat_history'] = []
    return render(request, 'rides/chatbot.html')



@staff_member_required
def admin_dashboard(request):
    # Get the current date and the first day of the current month
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)

    # Total Rides Created
    total_rides_created = Ride.objects.count()
    rides_created_this_month = Ride.objects.filter(ride_date__gte=first_day_of_month).count()

    # Total Rides Taken
    total_rides_taken = RideRequest.objects.filter(status='completed').count()
    rides_taken_this_month = RideRequest.objects.filter(
        status='completed',
        ride_date__gte=first_day_of_month
    ).count()

    # Calculate total profit for this month
    total_cost_this_month = RideRequest.objects.filter(
        status='completed',
        ride_date__gte=first_day_of_month
    ).aggregate(total_cost=Sum('cost'))['total_cost'] or Decimal('0')

    profit_this_month = total_cost_this_month * Decimal('0.1')  # 10% of the total cost

    rides = Ride.objects.all()

    popular_car_model = rides.values('car_model').annotate(count=Count('car_model')).order_by('-count').first()

    popular_route = rides.values('start_location', 'destination').annotate(route_count=Count('id')).order_by('-route_count').first()

    context = {
        'total_rides_created': total_rides_created,
        'rides_created_this_month': rides_created_this_month,
        'total_rides_taken': total_rides_taken,
        'rides_taken_this_month': rides_taken_this_month,
        'profit_this_month': profit_this_month.quantize(Decimal('0.01')),  # Round to 2 decimal places
        'popular_car_model': popular_car_model['car_model'] if popular_car_model else None,
        'popular_route': popular_route if popular_route else None,
    }

    return render(request, 'rides/admin_dashboard.html', context)



@staff_member_required
def visualization(request):
    # Total Rides Created and Taken
    total_rides_created = Ride.objects.count()
    total_rides_taken = RideRequest.objects.filter(status='completed').count()

    # Car Model Distribution
    car_model_data = RideGiver.objects.values('car').annotate(count=Count('car')).order_by('-count')
    car_models = [item['car'] for item in car_model_data]
    car_model_counts = [item['count'] for item in car_model_data]

    # Monthly Ride Trends
    six_months_ago = timezone.now().date() - timedelta(days=180)
    rides = Ride.objects.filter(ride_date__gte=six_months_ago)
    
    monthly_rides = defaultdict(int)
    for ride in rides:
        month_key = ride.ride_date.strftime("%Y-%m")
        monthly_rides[month_key] += 1
    
    sorted_monthly_rides = sorted(monthly_rides.items())
    months = [timezone.datetime.strptime(date, "%Y-%m").strftime("%B %Y") for date, _ in sorted_monthly_rides]
    monthly_ride_counts = [count for _, count in sorted_monthly_rides]

    # Top 5 Popular Routes
    top_routes_data = RideRequest.objects.values('start_location', 'destination') \
                        .annotate(count=Count('id')) \
                        .order_by('-count')[:5]
    
    top_routes = [f"{item['start_location']} to {item['destination']}" for item in top_routes_data]
    top_route_counts = [item['count'] for item in top_routes_data]

    context = {
        'total_rides_created': total_rides_created,
        'total_rides_taken': total_rides_taken,
        'car_models': car_models,
        'car_model_counts': car_model_counts,
        'months': months,
        'monthly_ride_counts': monthly_ride_counts,
        'top_routes': top_routes,
        'top_route_counts': top_route_counts,
    }

    return render(request, 'rides/visualization.html', context)



from django.db.models import F

def reports_view(request):
    # Get filter values from request
    filter_start_date = request.GET.get('start_date', '')
    filter_end_date = request.GET.get('end_date', '')
    
    # Apply filters if dates are provided
    rides = Ride.objects.all()
    ride_requests = RideRequest.objects.filter(status='completed')

    if filter_start_date:
        rides = rides.filter(ride_date__gte=filter_start_date)
        ride_requests = ride_requests.filter(ride_date__gte=filter_start_date)

    if filter_end_date:
        rides = rides.filter(ride_date__lte=filter_end_date)
        ride_requests = ride_requests.filter(ride_date__lte=filter_end_date)

    # Total rides created
    total_rides_created = rides.count()

    # Total rides taken
    total_rides_taken = ride_requests.count()

    # Total profit (10% of the total cost of completed rides)
    total_profit = ride_requests.aggregate(profit=Sum(F('cost') * Decimal('0.1')))['profit']

    # Most popular car model
    popular_car_model = rides.values('car_model').annotate(count=Count('car_model')).order_by('-count').first()

    # Most popular route
    popular_route = rides.values('start_location', 'destination').annotate(route_count=Count('id')).order_by('-route_count').first()

    context = {
        'total_rides_created': total_rides_created,
        'total_rides_taken': total_rides_taken,
        'total_profit': total_profit or 0,
        'popular_car_model': popular_car_model['car_model'] if popular_car_model else None,
        'popular_route': popular_route if popular_route else None,
        'filter_start_date': filter_start_date,
        'filter_end_date': filter_end_date,
    }
    return render(request, 'rides/reports.html', context)






@login_required
def sos_alert(request):
    if request.method == 'POST':
        user = request.user
        current_time = datetime.now()

        # Get current ride details
        try:
            # Check if user is a ride taker
            joined_ride = JoinedRide.objects.filter(
                request__user=user,
                request__status='joined',
                status='joined'
            ).first()

            if joined_ride:
                ride = joined_ride.ride
                ride_giver = ride.ride_giver
                ride_companions = JoinedRide.objects.filter(
                    ride=ride,
                    status='joined'
                ).exclude(request__user=user)

                # Prepare ride details
                ride_details = f"""
Emergency Alert from Ride Taker: {user.username}
User's Contact: {user.userprofile.mobile_number}
Time of Alert: {current_time}

Ride Details:
-------------
From: {ride.start_location}
To: {ride.destination}
Date: {ride.ride_date}
Time: {ride.ride_time}

Ride Giver Details:
------------------
Name: {ride_giver.user.username}
Contact: {ride_giver.user.userprofile.mobile_number}
Vehicle: {ride_giver.car}
Vehicle Number: {ride_giver.vehicle_number}

Ride Companions:
---------------
"""
                for companion in ride_companions:
                    ride_details += f"Name: {companion.request.user.username}\n"
                    ride_details += f"Contact: {companion.request.user.userprofile.mobile_number}\n\n"

            else:
                # Check if user is a ride giver
                ride = Ride.objects.filter(
                    ride_giver__user=user,
                    joinedride__status='joined'
                ).first()

                if ride:
                    ride_companions = JoinedRide.objects.filter(
                        ride=ride,
                        status='joined'
                    )

                    # Prepare ride details
                    ride_details = f"""
Emergency Alert from Ride Giver: {user.username}
User's Contact: {user.userprofile.mobile_number}
Time of Alert: {current_time}

Ride Details:
-------------
From: {ride.start_location}
To: {ride.destination}
Date: {ride.ride_date}
Time: {ride.ride_time}

Vehicle Details:
---------------
Car Model: {ride.car_model}
Vehicle Number: {ride.ride_giver.vehicle_number}

Ride Companions:
---------------
"""
                    for companion in ride_companions:
                        ride_details += f"Name: {companion.request.user.username}\n"
                        ride_details += f"Contact: {companion.request.user.userprofile.mobile_number}\n\n"

                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No active ride found'
                    })

            # Send email
            send_mail(
                subject='SHARERIDE - SOS ALERT!',
                message=ride_details,
                from_email='athul.23pmc116@mariancollege.org',
                recipient_list=['athulkjose001@gmail.com'],
                fail_silently=False,
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Emergency alert sent successfully'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })



def check_sos_status(request):
    ride_request_exists = RideRequest.objects.filter(user=request.user, status='joined').exists()
    ride_giver_with_joined = Ride.objects.filter(
        ride_giver=request.user, 
        ride_requests__status='joined'
    ).exists()

    sos_visible = ride_request_exists or ride_giver_with_joined
    return JsonResponse({'sos_visible': sos_visible})




@login_required
def report_user(request, user_id, ride_id):
    if request.method == 'POST':
        reported_user = get_object_or_404(User, id=user_id)
        ride = get_object_or_404(Ride, id=ride_id)
        reason = request.POST.get('reason')
        
        try:
            report = UserReport.objects.create(
                reported_user=reported_user,
                reporting_user=request.user,
                reason=reason,
                ride=ride
            )
            
            # Check if user has 2 or more reports
            report_count = UserReport.objects.filter(reported_user=reported_user).count()
            if report_count >= 2:
                user_profile = reported_user.userprofile
                user_profile.ban_user()
                messages.warning(request, "User has been banned due to multiple reports.")
            
            messages.success(request, "User has been reported successfully.")
        except IntegrityError:
            messages.error(request, "You have already reported this user for this ride.")
            
        return redirect('view_upcoming_rides')
    
    return render(request, 'rides/report_user.html', {
        'reported_user_id': user_id,
        'ride_id': ride_id
    })




def rate_user(request, user_id, ride_id):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        ride = get_object_or_404(Ride, id=ride_id)
        to_user = get_object_or_404(User, id=user_id)
        
        Rating.objects.create(
            from_user=request.user,
            to_user=to_user,
            ride=ride,
            rating=rating_value
        )
        
        messages.success(request, 'Rating submitted successfully!')
        return redirect('view_upcoming_rides')
        
    ride = get_object_or_404(Ride, id=ride_id)
    to_user = get_object_or_404(User, id=user_id)
    
    return render(request, 'rides/rate_user.html', {
        'to_user': to_user,
        'ride': ride
    })





@login_required
def message_list(request):
    """Displays a list of users with whom the current user has messaged."""
    user = request.user

    # Find all unique users the current user has sent messages to or received messages from
    sent_to = Message.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
    received_from = Message.objects.filter(receiver=user).values_list('sender', flat=True).distinct()

    # Combine the lists and remove duplicates
    all_users_ids = set(list(sent_to) + list(received_from))
    users = [User.objects.get(pk=user_id) for user_id in all_users_ids]

    # Count unread messages for each user
    unread_counts = {}
    for other_user in users:
        unread_counts[other_user.id] = Message.objects.filter(
            sender=other_user, receiver=user, is_read=False).count()

    context = {
        'users': users,
        'unread_counts': unread_counts,
    }
    return render(request, 'rides/message_list.html', context)


@login_required
def conversation(request, user_id):
    """Displays the conversation between the current user and another user."""
    other_user = get_object_or_404(User, id=user_id)
    user = request.user

    # Get all messages between the two users, ordered by timestamp
    messages = Message.objects.filter(
        Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
    ).order_by('timestamp')

    # Mark received messages as read  (Move this to AJAX)
    #Message.objects.filter(sender=other_user, receiver=user, is_read=False).update(is_read=True)

    context = {
        'other_user': other_user,
        'messages': messages,
    }
    return render(request, 'rides/conversation.html', context)


@login_required
def update_message_status(request, message_id, status_type):
    """Updates the message status (sent, delivered, read)."""
    try:
        message = Message.objects.get(pk=message_id, receiver=request.user)  # Only allow receiver to update
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found or unauthorized'})

    if status_type == 'delivered':
        message.delivered = True
    elif status_type == 'read':
        message.read = True
    message.save()

    return JsonResponse({'status': 'success'})


@csrf_exempt  # Only use this if you have CSRF issues with AJAX
def mark_messages_as_read(request, user_id):
    """Marks all unread messages from a specific user as read."""
    if request.method == 'POST':
        sender = get_object_or_404(User, id=user_id)
        receiver = request.user
        Message.objects.filter(sender=sender, receiver=receiver, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})