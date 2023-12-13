from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

#AUTH
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("", views.chatbot, name="chatbot"),
    path("delete-chats", views.delete_chats, name="delete_chats"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("json", views.import_json, name="json"),
    path("train", views.write_to_json, name="train"),
    
    
    ##APIs#####
    path("api/v1/all-chats/", views.ChatsList.as_view()),
    path("chat/<int:pk>/", views.ChatDetail.as_view()),
    
    ##Users Section
    path('api/v1/user-chats/', views.user_chat_list, name='user_chat_list'),
    
    ##Admin section
    path('api/v1/chatbot-system/', views.chatBot_system, name='chatBot_system'),
    path('api/v1/train-chatbot-system/', views.train_chatbot_system, name='train_chatbot_system'),
    
    ##AUTH
    path('api/v1/register/', views.register_users, name='register_users'),
    path('api/v1/login/', views.login_users, name='login_users'),
    # path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/v1/logout/', views.logout_users, name='logout_users'),
]

urlpatterns = format_suffix_patterns(urlpatterns)