from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
import re
from .models import Ride, RideGiver



class RideForm(forms.Form):
    start_location = forms.CharField(label='Start Location', max_length=255)
    destination = forms.CharField(label='Destination', max_length=255)


class RideCreateForm(forms.Form):
    start_location = forms.CharField(label='Start Location', max_length=255)
    destination = forms.CharField(label='Destination', max_length=255)



class RideGiverForm(forms.ModelForm):
    class Meta:
        model = RideGiver
        fields = ['car', 'features', 'fuel_type', 'vehicle_number']





class PasswordResetForm(forms.Form):
    email = forms.EmailField()



class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        # Check for at least one uppercase letter, one lowercase letter, and one special character
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Your password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Your password must contain at least one lowercase letter.")
        if not re.search(r'\W', password1):
            raise ValidationError("Your password must contain at least one special character.")

        # Check for at least 8 characters
        if len(password1) < 8:
            raise ValidationError("Your password must contain at least 8 characters.")

        # Bypass the password strength check
        self._check_password_strength = lambda password: None

        return password1

