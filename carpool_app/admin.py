from django.contrib import admin
from .models import JoinedRide, Ride, RideRequest, RideGiver
from django.contrib.auth.models import User, Group


admin.site.register(RideGiver)
admin.site.register(Ride)
admin.site.register(RideRequest)
admin.site.register(JoinedRide)


#admin.site.unregister(User)
admin.site.unregister(Group)
