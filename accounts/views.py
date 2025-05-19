from .forms import DonorPatientRegistrationForm, EligibilityForm, DonorProfileForm, PatientProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import User, BloodRequest, Donation
from django.shortcuts import render, redirect, get_object_or_404
from .utils import BLOOD_COMPATIBILITY
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').lower().strip()

        responses = {
            'salam': 'Wa Alaikum Assalam! Kaise madad kar sakta hoon?',
            'what is your name': 'I am DonateLife Bot.',
            'how to donate blood': 'Go to your dashboard and accept requests.',
            'who can donate blood': 'Healthy individuals aged 18–60 can donate.',
            'how often can I donate': 'You can donate every 3 months.',
            'where to find requests': 'Check your dashboard for pending requests.',
            'how to contact admin': 'Please use the contact form on the website.',
            'can i donate if i had covid': 'Wait at least 28 days after recovery.',
            'what is the minimum weight': 'Minimum weight to donate is 50kg.',
            'how long does donation take': 'Usually around 30–45 minutes.',
            'thank you': 'You’re welcome!',
            'bye': 'Goodbye! Stay safe.',
        }

        reply = responses.get(user_message, "Sorry, I didn't understand that. Try another question.")
        return JsonResponse({'reply': reply})


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@never_cache
def admin_dashboard(request):
    donors = User.objects.filter(role='donor')
    patients = User.objects.filter(role='patient')
    pending_requests = BloodRequest.objects.filter(status='pending')
    recent_donations = Donation.objects.order_by('-date')[:5]

    return render(request, 'accounts/admin_dashboard.html', {
        'donors': donors,
        'patients': patients,
        'pending_requests': pending_requests,
        'recent_donations': recent_donations,
    })

@login_required
def admin_all_donors(request):
    donors = User.objects.filter(role='donor')
    return render(request, 'accounts/admin_all_donors.html', {'donors': donors})

@login_required
def admin_all_patients(request):
    patients = User.objects.filter(role='patient')
    return render(request, 'accounts/admin_all_patients.html', {'patients': patients})

@login_required
def admin_all_requests(request):
    blood_requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_all_requests.html', {'requests': blood_requests})

@login_required
@never_cache
def patient_dashboard(request):
    user = request.user
    profile_complete = user.is_profile_complete()

    # pending_requests = BloodRequest.objects.filter(receiver=request.user, status='pending').order_by('-created_at')

    pending_requests = BloodRequest.objects.filter(sender=request.user, status='pending').order_by('-created_at')

    approved_requests = BloodRequest.objects.filter(sender=request.user, status='approved').order_by('-created_at')

    return render(request, 'accounts/patient_dashboard.html', {
        'user': user,
        'profile_complete': profile_complete,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests
    })

@login_required
def donor_dashboard(request):
    user = request.user
    
    if request.method == 'POST':
        form = DonorProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('donor_profile')  # Redirect to the same page or a success page
    else:
        form = DonorProfileForm(instance=user)

    profile_complete = all([
        user.age is not None,
        user.weight is not None,
        bool(user.blood_group),
        bool(user.city),
        user.last_donation_date is not None,
    ])


    pending_requests = BloodRequest.objects.filter(receiver=request.user, status='pending').order_by('-created_at')

    approved_requests = BloodRequest.objects.filter(receiver=request.user, status='approved').order_by('-created_at')

    context = {
        'form': form,
        'profile_complete': profile_complete,
        'username': user.username,
        'email': user.email,
        'age': user.age,
        'weight': user.weight,
        'blood_group': user.blood_group,
        'city': user.city,
        'last_donation_date': user.last_donation_date,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests
    }
    
    return render(request, 'accounts/donor_dashboard.html', context)

@login_required
def donor_received_requests(request):
    if request.user.role != 'donor':
        return redirect('home')  # optional: only allow donors

    received_requests = BloodRequest.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'accounts/donor_received_requests.html', {'received_requests': received_requests})

@login_required
def patient_requests(request):
    if request.user.role != 'patient':
        return redirect('home')

    sent_requests = BloodRequest.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'accounts/patient_requests.html', {'sent_requests': sent_requests})



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.role == 'donor':
                return redirect('donor_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')  # Django admin panel
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def register(request):
    if request.method == 'POST':
        form = DonorPatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save user but don't commit to DB yet
            user.role = form.cleaned_data['role']  # Set the role manually
            user.save()  # Now save to DB
            messages.success(request, 'Registration successful!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DonorPatientRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    User = get_user_model()
    total_donors = User.objects.filter(role='donor').count()
    total_patients = User.objects.filter(role='patient').count()
    return render(request, 'home.html', {
        'total_donors': total_donors,
        'total_patients': total_patients,
    })

def eligibility_view(request):
    if request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if (
                data['age'] >= 18 and
                data['weight'] >= 50 and
                data['good_health'] == True and
                data['tattoos_piercings'] == False and
                data['disqualifying_conditions'] == False
            ):
                result = "You are eligible to donate blood."
            else:
                result = "You are not eligible to donate blood at this time."
            return render(request, 'eligibility_result.html', {'result': result})
        else:
            # Form is invalid due to missing/invalid fields
            result = "Form submission is invalid. Please check all fields."
            return render(request, 'eligibility_result.html', {'result': result})
    else:
        form = EligibilityForm()
    return render(request, 'eligibility.html', {'form': form})


@login_required
def donor_profile(request):
    user = request.user
    if request.method == 'POST':
        form = DonorProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('donor_profile')
    else:
        form = DonorProfileForm(instance=user)

    return render(request, 'accounts/donor_profile.html', {'form': form})

@login_required
def patient_profile(request):
    user = request.user
    if user.role != 'patient':
        return redirect('home')  # Optional: restrict to only patients

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=user)

    return render(request, 'accounts/patient_profile.html', {'form': form})

@login_required
def admin_profile(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    return render(request, 'accounts/admin_profile.html', {'user': request.user})

def find_donor(request):
    query = request.GET.get('q')
    donors = []

    if query:
        donors = User.objects.filter(role='donor', city__icontains=query)

    return render(request, 'accounts/find_donor.html', {'donors': donors, 'query': query})

def request_blood(request, donor_id):
    donor = get_object_or_404(User, id=donor_id, role='donor')

    # Compatibility check
    user_blood_group = request.user.blood_group
    compatible_groups = BLOOD_COMPATIBILITY.get(user_blood_group, [])
    is_compatible = donor.blood_group in compatible_groups

    if request.method == 'POST':
        urgency = request.POST.get('urgency')
        message = request.POST.get('message')

        if not is_compatible:
            messages.error(request, "Warning: This donor's blood group is NOT compatible with yours.")
            return redirect('request_blood', donor_id=donor.id)

        BloodRequest.objects.create(
            sender=request.user,
            receiver=donor,
            urgency=urgency,
            message=message
        )

        messages.success(request, "Your blood request has been sent successfully.")
        return redirect('patient_dashboard')

    context = {
        'donor': donor,
        'is_compatible': is_compatible,
        'compatibility_message': (
            "These blood types are compatible! This donor can donate blood to you."
            if is_compatible else
            "Warning: This donor's blood group is NOT compatible with yours."
        )
    }

    return render(request, 'accounts/request_blood.html', context)

def approve_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        blood_request.status = 'approved'
        blood_request.save()
    
        messages.success(request, 'Request approved successfully.')

    return redirect('admin_dashboard')  # replace with your dashboard view name


def reject_request(request, request_id):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        blood_request.status = 'rejected'
        blood_request.save()
        messages.error(request, 'Request rejected.')
    return redirect('admin_dashboard')