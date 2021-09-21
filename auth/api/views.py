from asyncio import tasks
from django.shortcuts import render
from django.http import JsonResponse, response
from django.http import HttpResponse
from django.db.models import Q
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import  IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth.models import Group,User
from django.contrib.auth import authenticate,login,logout
from .forms import CreateUserForm
from api import forms, serializers
import random
import asyncio
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
from django.urls import reverse
from threading import Thread
from django.urls import resolve
from django.contrib.sites.models import Site
from django.utils.functional import SimpleLazyObject
from django.conf import settings
import urllib
from django.core.mail import EmailMultiAlternatives

sec_alfanumeric = '0123456789abcdefghijklmnopqrstuvwxzyABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Create your views here.
# Create your views here.
@api_view(['GET'])
def api_overview(request):
    api_url = {
        'Auth Login':'/auth-list/',
        'Auth Register':'/auth-register/',
    }
    return Response(api_url)

@api_view(['GET'])
def userList(request):
    user = User.objects.all()
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def authentication(request):
    fetch  = request.data
    try:
        uname = fetch["username"]
        pwd = fetch["password"]
        user = authenticate(request,username=uname, password = pwd)
        group = user.groups.all()[0].name
        if user is not None and group == 'management':
            stat =  User.objects.filter(username = user).values()[0]['is_active'] #get Status activation
            
            response = JsonResponse(data= {
                'message':"Access Successfuly",
                'status_code':200,
                'auth_value':stat,
            })
            response.status_code = 200
        elif group != 'management':
            response = JsonResponse(data= {
                'message':"Not Authorized",
                'status_code':401,
                'auth_value':False,
            })
            response.status_code = 401
        
    except:
        response = JsonResponse(data= {
            'message':"Something went Wrong, Check your Username or Password",
            'status_code':406,
            'auth_value':False,
        })
        response.status_code = 406

    return response


#resigter API
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def registration(request):
    fetch = request.data
    try:
        uname = fetch["username"]
        email = fetch["email"]
        pwd1 = fetch["password1"]
        pwd2 = fetch["password2"]
        secret = ''.join(random.choice(sec_alfanumeric) for i in range(16))

        req_form = {
            'csrfmiddlewaretoken':secret,
            'username':uname,
            'email':email,
            'password1':pwd1,
            'password2':pwd2
        }
        form = CreateUserForm(req_form)
        if form.is_valid():
            usr = form.save(commit = False)
            usr.is_active = False
            usr.save()
            mailing(request,usr)
            resp = "Form Valid"
            ssts_code = 200
            msg = "Register Successfuly kindly Check your Email for Verification" 
        else:
            msg = "Registration Failed" 
            ssts_code = 406
            resp = form.errors

        response = JsonResponse(data= {
                'message':msg,
                'status_code':ssts_code,
                'auth_value':resp,
            })
        response.status_code = ssts_code
    except:
        response = JsonResponse(data= {
            'message':"Something went Wrong, Check your Username or Password",
            'status_code':406,
            'auth_value':"Registration Error",
        })
        response.status_code = 406

    return response


#Bikin microservices Email.
def mailing(request,usr):
    #auth Logic
    pesan = ''
    curr_site = request.build_absolute_uri('/')[:-1].strip("/")
    email_body = {
            'user': usr,
            'domain': curr_site,
            'uid': urlsafe_base64_encode(force_bytes(usr.pk)),
            'token': account_activation_token.make_token(usr),
        }
    print(email_body["token"], email_body["uid"])
    active_url = curr_site+"/auth/activate/"+email_body['uid']+"/"+email_body["token"]
    
    email_subject = 'Activate your account'
    try:
        email_body = """\
            <html>
            <head></head>
            <body>
                <h2>%s</h2>
                <p>Please the link below to activate your account <a href="%s">Verification Link</a></p>
                
            </body>
            </html>
            """ % (usr.username, active_url,)
        email = EmailMessage(email_subject, email_body, to=[usr.email])
        email.content_subtype = "html" # this is the crucial part 
        email.send()
        pesan = 'Activation Email has send'
    except:
        pesan = "Failed to send the Verification email."
    print(pesan)
    

def emailverification(request,uidb64,token):
    msg = ''
    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=id)
        if account_activation_token.check_token(user, token):           
            user.is_active = True
            user.save()
            msg= 'Activation Success'

    except Exception as ex:
        msg = 'Activation Fail'
    return HttpResponse("html")
