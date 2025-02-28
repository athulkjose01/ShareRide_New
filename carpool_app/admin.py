from django.contrib import admin
from .models import JoinedRide, Rating, Ride, RideRequest, RideGiver, RideRequestTemporary, UserReport, UserProfile, Message
from django.contrib.auth.models import User, Group


admin.site.register(RideGiver)
admin.site.register(Ride)
admin.site.register(RideRequest)
admin.site.register(JoinedRide)
admin.site.register(UserReport)
admin.site.register(UserProfile)
admin.site.register(Rating)
admin.site.register(Message)
admin.site.register(RideRequestTemporary)


#admin.site.unregister(User)
admin.site.unregister(Group)
