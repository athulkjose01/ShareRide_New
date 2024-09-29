from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os
import re
from django.views import View
import googlemaps
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
from .forms import RideForm
from .models import JoinedRide, Ride, RideRequest, UserProfile
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
from django.http import JsonResponse
from django.shortcuts import render



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
            
            if user.is_superuser and user.username == 'admin':
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

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            error_message = "This username is already taken. Please choose a different one."
            return render(request, 'rides/register.html', {'error_message': error_message})
        
         # Check if the mobile number is already taken
        if UserProfile.objects.filter(mobile_number=mobile_number).exists():
            error_message = "This mobile number is already associated with another account."
            return render(request, 'rides/register.html', {'error_message': error_message})

        if User.objects.filter(email=email).exists():
            error_message = "This email is already taken. Please use a different one."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Email format check using regular expressions
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message = "Invalid email format. Please enter a valid email address."
            return render(request, 'rides/register.html', {'error_message': error_message})

        # Create the user and save it
        myuser = User.objects.create_user(username=username, email=email, password=password)
        myuser.first_name = name
        myuser.save()

        # Update the UserProfile mobile_number (profile is already created via the signal)
        user_profile = UserProfile.objects.get(user=myuser)
        user_profile.mobile_number = mobile_number
        user_profile.save()

        return redirect('login')

    return render(request, 'rides/register.html')



class LogoutView(LogoutView):
    next_page = 'match_rides' 





def home(request):
    form = RideForm()
    return render(request, 'rides/ride_taker.html', {'form': form})



@login_required
def save_route(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start = data.get('start')
        destination = data.get('destination')
        polyline = data.get('polyline')
        date = data.get('ride_date')
        time = data.get('ride_time')

        # Get the RideGiver for the currently logged-in user
        try:
            ride_giver = RideGiver.objects.get(user=request.user)
        except RideGiver.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'RideGiver not found for the current user'})

        # Create a new Ride object
        Ride.objects.create(
            ride_giver=ride_giver,
            start_location=start,
            destination=destination,
            polyline=polyline,
            ride_date=date,
            ride_time=time,
            car_model=ride_giver.car,  # Set car_model from RideGiver's car
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'})






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
            form = RideForm()
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



def match_rides(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start = data['start']
        destination = data['destination']
        polyline = data['polyline']
        date = data['date']
        time = data['time']

        # Decode and round the polyline coordinates
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        decoded_polyline = googlemaps.convert.decode_polyline(polyline)
        rounded_polyline = [(round(point['lat'], 1), round(point['lng'], 2)) for point in decoded_polyline]

        # Get the start and end locations from the polyline
        start_location = rounded_polyline[0]
        end_location = rounded_polyline[-1]

        # Calculate distance using Google Maps API
        directions_result = gmaps.directions(start_location, destination, mode="driving")

        if directions_result:
            distance = directions_result[0]['legs'][0]['distance']['value'] / 1000  # Convert meters to kilometers
        else:
            distance = 0  # Default to 0 if unable to calculate

        today = datetime.now().date()
        now_time = datetime.now().time()

        # Initialize matched_rides list
        matched_rides = []

        # Apply conditional filtering based on the date
        ride_queryset = Ride.objects.filter(
            ride_date=date  # Match the ride date
        ).annotate(
            joined_count=Count('joinedride')  # Annotate rides with the number of joined rides
        ).filter(
            joined_count__lt=5  # Only include rides with less than 5 joined rides
        )

        # If the date is today, filter by time
        if date == str(today):
            ride_queryset = ride_queryset.filter(Q(ride_time__gte=now_time) & Q(ride_time__gte=time))
        else:
            ride_queryset = ride_queryset.filter(ride_time__gte=time)

        # Iterate over matched rides and apply polyline matching
        for ride in ride_queryset:
            ride_decoded_polyline = googlemaps.convert.decode_polyline(ride.polyline)
            ride_rounded_polyline = [(round(point['lat'], 1), round(point['lng'], 2)) for point in ride_decoded_polyline]

            # Check if both start and end points are in the ride giver's polyline and in the correct order
            start_index = -1
            end_index = -1
            for i, point in enumerate(ride_rounded_polyline):
                if point == start_location:
                    start_index = i
                if point == end_location:
                    end_index = i
                if point == end_location and start_index != -1 and end_index != -1:
                    break

            if start_index != -1 and end_index != -1 and start_index < end_index:
                # Situation 1: Ride taker needs to travel more from the drop-off location
                last_common_point = ride_rounded_polyline[end_index]
                ride_taker_travel_more = end_location != last_common_point

                # Situation 2: Ride giver needs to travel more from the drop-off location
                ride_giver_travel_more = ride.destination != last_common_point

                # Add matched ride to the list
                matched_rides.append({
                    'ride_giver_start': ride.start_location,
                    'ride_taker_start': start,
                    'ride_taker_destination': destination,
                    'ride_giver_destination': ride.destination,
                    'last_common_point': last_common_point,
                    'ride_taker_travel_more': ride_taker_travel_more,
                    'ride_giver_travel_more': ride_giver_travel_more,
                    'ride': ride, 
                    'date': date,
                    'time': time,
                    'distance': distance,
                })

        # Render the results template
        return render(request, 'rides/ride_taker_results.html', {'matched_rides': matched_rides})

    # Return fail status if the request method is not POST
    return JsonResponse({'status': 'fail'})




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


@csrf_exempt
def predict_cost(request):
    if request.method == 'POST':
        distance = float(request.POST.get('distance'))
        car_model = request.POST.get('car_model')
        fuel_type = request.POST.get('fuel_type')

        # Encode the inputs
        car_model_encoded = label_encoder_model.transform([car_model])[0]
        fuel_type_encoded = label_encoder_fuel.transform([fuel_type])[0]
        
        # Prepare the input for prediction
        X_input = np.array([[car_model_encoded, fuel_type_encoded, distance]])

        
        # Make prediction
        predicted_cost = model.predict(X_input)[0]
        
        return JsonResponse({'predicted_cost': predicted_cost})
    
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
        fuel_type = request.POST.get('fuel_type')
        mobile_number = request.POST.get('mobile_number')
        features = request.POST.get('features')

        form = RideForm()  # Create a blank form or use this according to your flow

        try:
            # Attempt to create and save RideGiver
            RideGiver.objects.create(user=user, car=car, fuel_type=fuel_type, features=features, mobile_number=mobile_number)
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
    tomorrow = datetime.now().date() + timedelta(days=1)


    user_rides_today = Ride.objects.filter(
         ride_giver__user=request.user,
         ride_date=today,
         ride_time__gte=now_time)

    user_rides_future = Ride.objects.filter(
         ride_giver__user=request.user,
         ride_date__gt=today)

    # Combine the two querysets using union
    user_rides = user_rides_today.union(user_rides_future).order_by('-ride_date', '-ride_time')

    user = request.user
    
    travel_companions = JoinedRide.objects.filter(
        Q(ride__ride_giver=ride_giver) | Q(request__user=user),
        ride__ride_date__gte=today
    )

    # Prepare a dictionary to hold unique rides and their companions
    unique_rides = {}
    for companions in travel_companions:
        ride = companions.ride
        if ride not in unique_rides:
            unique_rides[ride] = {
                'ride_giver': ride.ride_giver.user.username,
                'companions': []
            }
        unique_rides[ride]['companions'].append(companions.request.user.username)
 

    # Apply different filters based on whether the ride date is today or in the future
    user_requested_rides_today = RideRequest.objects.filter(
        user=request.user,
        ride__ride_date=today,
        ride__ride_time__gte=now_time,
        status__in=['requested', 'accepted']
    ).exclude(id__in=JoinedRide.objects.values_list('request_id', flat=True))

    user_requested_rides_future = RideRequest.objects.filter(
        user=request.user,
        ride__ride_date__gt=today,
        status__in=['requested', 'accepted']
    ).exclude(id__in=JoinedRide.objects.values_list('request_id', flat=True))

    # Combine the two querysets using union
    user_requested_rides = user_requested_rides_today.union(user_requested_rides_future).order_by('-ride_date', '-ride_time')


    joined_rides = JoinedRide.objects.filter(
        request__user=request.user,
        status='joined',
        ride__ride_date__in=[today, tomorrow]
    )

    context = {
        'user_rides': user_rides,
        'user_requested_rides': user_requested_rides,
        'joined_rides': joined_rides,
        'travel_companions': travel_companions,
        'unique_rides': unique_rides,
    }

    return render(request, 'rides/upcoming_rides.html', context)



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

        return context

    def post(self, request, *args, **kwargs):
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
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





genai.configure(api_key=settings.GEMINI_API_KEY)
chatbot_model = genai.GenerativeModel('gemini-pro')

def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        
        response = chatbot_model.generate_content(user_input)
        
        return JsonResponse({'response': response.text})
    
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

