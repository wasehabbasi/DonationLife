from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model  # ✅ correct import
from .models import User
from datetime import date, timedelta


User = get_user_model()  # ✅ use this to get 'accounts.User'

class DonorPatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    role_choices = [
        ('donor', 'Blood Donor'),
        ('patient', 'Patient'),
    ]
    role = forms.ChoiceField(choices=role_choices, widget=forms.RadioSelect, required=True)

    class Meta:
        model = User  # ✅ now this points to accounts.User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class EligibilityForm(forms.Form):
    age = forms.IntegerField(
        label='Age',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Must be between 18 and 65'
    )
    weight = forms.FloatField(
        label='Weight (kg)',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Must be at least 50 kg (110 lbs)'
    )
    good_health = forms.BooleanField(label='Are you in good health?', required=True)
    last_donation_date = forms.DateField(
        label='Last Donation Date (if applicable)',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    tattoos_piercings = forms.BooleanField(
        label='Have tattoos or piercings in the last 6 months?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    disqualifying_conditions = forms.BooleanField(
        label='Do you have disqualifying conditions (HIV, Hepatitis, etc.)?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get("age")
        weight = cleaned_data.get("weight")
        last_donation = cleaned_data.get("last_donation_date")
        tattoos = cleaned_data.get("tattoos_or_piercings")
        disqualified = cleaned_data.get("disqualifying_conditions")

        if age is not None and not (18 <= age <= 65):
            self.add_error('age', "Age must be between 18 and 65.")

        if weight is not None and weight < 50:
            self.add_error('weight', "Weight must be at least 50 kg (110 lbs).")

        if last_donation and (date.today() - last_donation) < timedelta(weeks=8):
            self.add_error('last_donation_date', "Last donation must be at least 8 weeks ago.")

        if tattoos:
            self.add_error('tattoos_piercings', "Cannot donate due to recent tattoos or piercings.")

        if disqualified:
            self.add_error('disqualifying_conditions', "You are not eligible due to medical conditions.")

class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'age',
            'weight',
            'blood_group',
            'city',
            'last_donation_date',
            'is_healthy',
            'has_tattoos_or_piercings',
            'has_disqualifying_conditions',
        ]
        widgets = {
            # 'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_healthy': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_tattoos_or_piercings': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_disqualifying_conditions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Adding custom fields for health-related questions
    is_healthy = forms.BooleanField(required=False, label="Are you in good health?")
    has_tattoos_or_piercings = forms.BooleanField(required=False, label="Do you have any tattoos or piercings in the last 6 months?")
    has_disqualifying_conditions = forms.BooleanField(required=False, label="Do you have any disqualifying medical conditions?")

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['age', 'blood_group', 'city', 'medical_condition']

        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_condition': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your medical condition (if any)'
            }),
        }