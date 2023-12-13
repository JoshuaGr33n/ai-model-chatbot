from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User, Group
from .models import Chat
from django.utils import timezone
import json
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.renderers import JSONRenderer

##Exceptions
from django.db import IntegrityError
from django.core.exceptions import ValidationError

##API
from rest_framework import generics, status
from .serializers import ChatSerializer, RegistrationSerializer
from django.core.serializers import serialize
from templatetags.custom_template_tags import time_ago, current_user

#AUTH
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .authentication import token_expire_handler, expires_in


from django.contrib.auth import get_user_model
User = get_user_model()



openai_api_key = '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'
openai.api_key = openai_api_key


# text completion
# def ask_openai(message):
#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=generate_prompt(message), #message,
#         max_tokens=150,
#         n=1,
#         stop=None,
#         temperature=0.7,
#     )

# #    print(response)
#     answer = response.choices[0].text.strip()
#     return answer
# def generate_prompt(animal):
#       return """
#       Everything about farming
#       Question: {}
#       Answer:""".format(
#             animal.capitalize()
#          )


def import_json():
    f = open('files/data.json')
    
    data = json.load(f)

    return data['descriptor']
 

# chat completion
def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",  # "gpt-4",
        messages=[
            {"role": "system", "content": import_json()},
            {"role": "user", "content": message},
        ]
    )

    # print(response)
    answer = response.choices[0].message.content.strip()
    return answer


# Create your views here.

def write_to_json(request):
   if request.user.is_authenticated == False:
        return redirect("/logout")
    
   if request.method == 'POST':
      try:
         jsonFile = open("files/data.json", "r") 
         data = json.load(jsonFile)
         jsonFile.close()

         data["descriptor"] = request.POST['description']
         
         jsonFile = open("files/data.json", "w+")
         jsonFile.write(json.dumps(data))
         jsonFile.close()
         
         success_message = "Success"
         return render(request, "train.html", {'success_message': success_message, 'descriptor': import_json()})  
      except:
               error_message = 'Error Creating Description'
               return render(request, "train.html", {'error_message': error_message})  
   else:
     return render(request, "train.html", {'descriptor': import_json()})


def chatbot(request):
     if request.user.is_authenticated == False:
        return redirect("/logout")

     chats = Chat.objects.filter(user=request.user)
     if request.method == 'POST':
         message = request.POST.get('message')
         response = ask_openai(message)
         created_at=timezone.now()

         chat = Chat(user=request.user, message=message,
                     response=response, created_at=timezone.now())
         chat.save()
         return JsonResponse({'message': message, 'response': response, 'created_at': time_ago(created_at)})

     return render(request, "chatbot.html", {'chats': chats})
  
def delete_chats(request):  
      Chat.objects.filter(user=request.user).delete()
      return redirect('chatbot')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid Phone Number and Password'
            return render(request, "login.html", {'error_message': error_message})
    else:
        return render(request, "login.html")


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                # user = User.objects.create_user(username, email, password1)
                
                user = User(username=username,phone=phone,email=email,password=password1,is_superuser=0,first_name=first_name,last_name=last_name)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error Creating Account'
                return render(request, "register.html", {'error_message': error_message})

        else:
            error_message = 'Password Dont Match!'
            return render(request, "register.html", {'error_message': error_message})

    return render(request, "register.html", {})


def logout(request):
    auth.logout(request)
    return redirect('login')
 
 
 
 
####APIs########     
@api_view(["POST"])
@permission_classes([AllowAny])
def register_users(request):
    try:
        data = {}
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            account.password = make_password(request.data.get("password"))
            account.is_active = True
            account.save()
            token = Token.objects.get_or_create(user=account)[0].key
            is_expired, token = token_expire_handler(token) 
            data["message"] = "User Registered Successfully"
            data["email"] = account.email
            data["username"] = account.username
            data["fullname"] = account.first_name+' '+account.last_name
            data["token"] = token
            data["token_expires_in"] = expires_in(token)
        else:
            data = serializer.errors
            
        return Response(data)
    except IntegrityError as e:
        account=User.objects.get(username='')
        account.delete()
        raise ValidationError({"400": f'{str(e)}'})

    except KeyError as e:
        print(e)
        raise ValidationError({"400": f'Field {str(e)} missing'})
 
 
 
@api_view(["POST"])
@permission_classes([AllowAny])
def login_users(request):

        data = {}
        reqBody = json.loads(request.body)
        username = reqBody['username']
        password = reqBody['password']
        try:

            user = User.objects.get(username=username)
        except BaseException as e:
            return JsonResponse({'Error': "Incorrect Login credentials"}, status=status.HTTP_401_UNAUTHORIZED) 

        
        
        if not check_password(password, user.password):
            return JsonResponse({'Error': "Incorrect Login credentials"}, status=status.HTTP_401_UNAUTHORIZED) 
         
        token = Token.objects.get_or_create(user=user)[0].key
        is_expired, token = token_expire_handler(token) 
        # print(token)
        if user:
            if user.is_active:
                auth.login(request, user)
                data["message"] = "User Logged in"
                data["email_address"] = user.email
                data["name"] = user.first_name+' '+user.last_name

                Res = {"data": data, "token": token, 'expires_in': expires_in(token)}
                

                return Response(Res)
            else:
                raise ValidationError({"400": f'Account not active'})
        else:
            raise ValidationError({"400": f'Account doesnt exist'})     

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout_users(request):

    request.user.auth_token.delete()
    logout(request)
    return Response('User Logged out successfully')  


class ChatsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    def get_salary(self):
        queryset = Chat.objects.all()


class ChatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_chat_list(request):
    token = Token.objects.get_or_create(user=request.user)[0].key
    is_expired, token = token_expire_handler(token) 
    try:
        # serializer = ChatSerializer(data=request.data)
        chats = Chat.objects.filter(user_id=request.user.id).order_by('-id')
        data = []
        if chats.count() > 0:
            for chat in chats:
                d = {
                "id":   chat.id,    
                "user":   chat.message,
                "chatbot": chat.response,
                "date":   time_ago(chat.created_at)
                }
                
                data.append(d)
             # return Response(json.dumps(data)) 
            return JsonResponse({'count':chats.count(),'results':data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'results':'No Chats'}, status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        return JsonResponse({'status':'Error', 'message':{str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


########APIs Admin Section########    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chatBot_system(request):  
    if request.user.is_superuser == 0:
        request.user.auth_token.delete()
        logout(request)
        return Response({'Error':'Not Allowed'}, status=status.HTTP_401_UNAUTHORIZED)    
    return JsonResponse({'system':import_json()}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def train_chatbot_system(request):
    if request.user.is_superuser == 0:
        request.user.auth_token.delete()
        logout(request)
        return Response({'Error':'Not Allowed'}, status=status.HTTP_401_UNAUTHORIZED) 
    else:
        try:
            jsonFile = open("files/data.json", "r") 
            data = json.load(jsonFile)
            jsonFile.close()

            data["descriptor"] = request.data.get("description")
            
            jsonFile = open("files/data.json", "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
            
            success_message = "Success"
            return JsonResponse({'success_message': success_message, 'descriptor': import_json()}, status=status.HTTP_200_OK)  
        except:
            error_message = 'Error Creating Description'
            return JsonResponse({'Error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

  




  
    