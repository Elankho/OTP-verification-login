from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import User
from django.utils import timezone
import random
import jwt


@csrf_exempt
@require_POST
def generate_otp(request):
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required.'}, status=400)

    try:
        user = User.objects.get(email=email)
        # Check if the user is blocked due to consecutive wrong attempts
        if user.wrong_attempts >= 5:
            block_time = user.block_timestamp + timezone.timedelta(hours=1)
            if block_time > timezone.now():
                return JsonResponse({'error': 'Account is blocked. Please try again later.'}, status=403)

        # Check the time gap between OTP generation requests
        min_time_gap = user.otp_timestamp + timezone.timedelta(minutes=1)
        if min_time_gap > timezone.now():
            time_diff = min_time_gap - timezone.now()
            seconds = time_diff.total_seconds()
            return JsonResponse({'error': f'Please wait for {seconds} seconds before generating a new OTP.'}, status=429)

        # Generate OTP and update user data
        otp = generate_otp_code()
        user.otp = otp
        user.otp_timestamp = timezone.now()
        user.save()
    except User.DoesNotExist:
        # Create a new user if it doesn't exist
        otp = generate_otp_code()
        user = User.objects.create(email=email, otp=otp, otp_timestamp=timezone.now())

    # Send OTP to the user's email
    send_otp_email(user.email, user.otp)

    return JsonResponse({'message': 'OTP has been generated and sent to your email.'})


@csrf_exempt
@require_POST
def login(request):
    email = request.POST.get('email')
    otp = request.POST.get('otp')
    if not email or not otp:
        return JsonResponse({'error': 'Email and OTP are required.'}, status=400)

    try:
        user = User.objects.get(email=email)
        # Check if the user is blocked due to consecutive wrong attempts
        if user.wrong_attempts >= 5:
            block_time = user.block_timestamp + timezone.timedelta(hours=1)
            if block_time > timezone.now():
                return JsonResponse({'error': 'Account is blocked. Please try again later.'}, status=403)

        # Check if the OTP is valid and within the time limit (5 minutes)
        if otp != user.otp or user.otp_timestamp + timezone.timedelta(minutes=5) < timezone.now():
            user.wrong_attempts += 1
            user.save()
            if user.wrong_attempts >= 5:
                user.block_timestamp = timezone.now()
                user.save()
                return JsonResponse({'error': 'Invalid OTP. Account is blocked. Please try again later.'}, status=403)
            else:
                return JsonResponse({'error': 'Invalid OTP.'}, status=401)

        # Reset wrong_attempts and block_timestamp since the OTP is valid
        user.wrong_attempts = 0
        user.block_timestamp = None
        user.save()

        # Generate and return a JWT token
        token = generate_jwt_token(user.email)
        return JsonResponse({'token': token})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid email.'}, status=401)


def send_otp_email(email, otp):
    subject = 'OTP Verification'
    message = f'Your OTP is: {otp}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def generate_otp_code():
    # Replace this function with your OTP generation logic
    return str(random.randint(100000, 999999))


def generate_jwt_token(email):
    # Replace this function with your JWT token generation logic
    payload = {
        'email': email,
        'exp': timezone.now() + timezone.timedelta(minutes=15)  # Set expiration time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token.decode('utf-8')


def home(request):
    return HttpResponse("Welcome to the OTP Verification App!")
