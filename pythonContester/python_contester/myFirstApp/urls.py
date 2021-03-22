from django.urls import path
from . import views
from python_contester import settings
from django.contrib.auth.views import LogoutView
from django.urls import *



urlpatterns = [
    # localhost/index
    path('', views.index, name = 'index'),
    # currentTask/task_id
    path('currentTask <int:task_id>', views.currentTask, name='currentTask'),
    # localhost/moreProblems
    path('moreProblems', views.moreProblems, name = 'moreProblems'),
    # localhost/currentTask/code
    path('currentTask <int:task_id> code', views.addCode, name = 'addCode'),
    # localhost/forum
    path('forum', views.forum, name = 'forum'),
    # localhost/ask
    path('ask', views.ask, name = 'ask'),
    # localhost/addQuestion
    path('addQuestion', views.addQuestion, name = 'addQuestion'),
    # localhost/question
    path('question <int:id>', views.question, name = 'question'),
    # localhost/addAnswer/id
    path('addAnswer <int:id>', views.addAnswer, name = 'addAnswer'),
    # localhost/rating
    path('rating', views.rating ,name ='rating' ),
    # localhost/userpage
    path('userpage', views.userpage ,name = 'userpage'),
    # localhost/register
    path('register', views.register,name='register'),
    # localhost/user_login
    path('user_login', views.user_login, name='user_login'),
    # localhost/user_logout
    path('user_logout', LogoutView.as_view(next_page = reverse_lazy('index')), name = 'user_logout'),
]
