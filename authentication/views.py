from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth


def activate_account(request, username):

    pass

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})
    

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alpha numeric characters'}, status = 400)
        if User.objects.filter(username = username).exists():
            return JsonResponse({'username_error':'sorry this username already exists, choose another one'}, status = 409)
        return JsonResponse({"username_valid":True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        
        user = User.objects.create_user(username, email, password)
        user.save()


        print(username, email, password)

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(request, 'Password is too short')
                    return render(request, 'authentication/register.html', context)

                user.is_active = False

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

                activate_url = "http://"+domain+link
                email_subject = 'Activate your account'
                email_body = "Hi "+user.username+", Please use this link to verify this account\n"+activate_url
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]

                send_mail(
                    email_subject,
                    email_body,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )  
        messages.success(request, 'Account Activated successfully')
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk = id)

            if not token_generator.check_token(user, token):
                return redirect("login"+"?message="+'User already activated')

            if user.is_active:
                return redirect("login")
            user.is_active = True
            user.save()
            messages.success(request, 'Account Activated successfully')
            return redirect('login')
        except Exception as ex:
            pass

        return redirect("login")

class LoginView(View):
    def get(self, request):
        return render(request,"authentication/login.html")
    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username , password=password)
            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome,'+ user.username +'you are logged in' )
                    return redirect('expenses')

                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')
        messages.error(
            request, 'Please fill all fields')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request.user)
        messages.success(request, 'You have been logged out')
        return redirect('login')
