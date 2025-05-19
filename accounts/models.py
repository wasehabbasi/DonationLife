from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Blood Donor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ], null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)

    # Add this instead for patients
    medical_condition = models.TextField(null=True, blank=True)

    def is_profile_complete(self):
        if self.role == 'donor':
            required_fields = [
                self.age, self.weight, self.blood_group, self.city,
                self.last_donation_date
            ]
        elif self.role == 'patient':
            required_fields = [
                self.age, self.blood_group, self.city, self.medical_condition
            ]
        else:
            return True  # Admins don't require this

        return all(field is not None and field != '' for field in required_fields)

    def __str__(self):
        return self.username

class BloodRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    urgency = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, related_name='received_donations', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.donor} donated to {self.patient} on {self.date}"

# class DonationHistory(models.Model):
#     donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
#     patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_donations')
#     date_donated = models.DateField(auto_now_add=True)
#     blood_amount_ml = models.PositiveIntegerField(default=450)
#     location = models.CharField(max_length=100, default='Unknown')
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.donor.username} donated on {self.date_donated}"
