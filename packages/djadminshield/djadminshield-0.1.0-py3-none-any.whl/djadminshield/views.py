from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
import logging
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import login
from user_agents import parse
from .models import UnauthorizedAccessAttempt

logger = logging.getLogger(__name__)


# Function to get the client ip address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def fake_admin_login(request):
    if request.method == 'POST':
        
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        parsed_agent = parse(user_agent)
        
        # To get client browser information
        browser = parsed_agent.browser.family
        # To get client os information
        os = parsed_agent.os.family
        # To get device type. Ex- Desktop, Mobile or Tablet
        device_type = 'Mobile' if parsed_agent.is_mobile else 'Tablet' if parsed_agent.is_tablet else 'Desktop' 
        # To get clients preferable languages
        languages = request.META.get('HTTP_ACCEPT_LANGUAGE', 'unknown')
        
        # Get the current time of the login attempt
        attempt_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ip = get_client_ip(request)
        logger.warning(f"Unauthorized admin login attempt from IP: {ip} at {attempt_time}. Browser: {browser}, OS: {os}, Device Type: {device_type}, Prefer Languages: {languages}.")
        
        # Check the credentials even if they are incorrect
        form = AuthenticationForm(request, data=request.POST)
        
        # Manually authenticate to ensure we mimic the error handling
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # If the credentials are correct, but we don't want to log the hacker in,
            # We can return an error message as we don't want to allow un-authorized access.
            # form.add_error(None, "Invalid Credentials, please try again.")  # Add a fake error
            # Log the incorrect login attempts as warning
            description = f"Incorrect login attempt with correct username and password from IP: {ip}"
            form.add_error(None, "Please enter a correct username and password. Note that both fields may be case-sensitive.") # Add an error message
            logger.warning(f"Incorrect login attempt with correct username from IP: {ip}")
            UnauthorizedAccessAttempt.objects.create(
                ip_address=ip,
                attempt_time=attempt_time,
                browser=browser,
                os=os,
                device_type=device_type,
                prefer_languages=languages,
                description=description,
            )
            
        else:
            # If credentials are incorrect, show the error
            # form.add_error(None, "Invalid credentials, please try again.") # Add an error message
            description = f"Incorrect login attempt with incorrect username from IP: {ip}"
            logger.warning(f"Incorrect login attempt with incorrect username from IP: {ip}")
            UnauthorizedAccessAttempt.objects.create(
                ip_address=ip,
                attempt_time=attempt_time,
                browser=browser,
                os=os,
                device_type=device_type,
                prefer_languages=languages,
                description=description,
            )
            
        return render(request, 'djadminshield/admin/login.html', {'form': form})
    
    else:
        form = AuthenticationForm()
        
    return render(request, 'djadminshield/admin/login.html', {'form': form})