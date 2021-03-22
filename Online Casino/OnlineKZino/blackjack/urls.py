from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from django.views.generic import DetailView
from django.conf.urls.static import static
from django.conf import settings

from Menu import views
from Menu.views import TopU

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',views.index,name='index'),
    url(r'^special/',views.special,name='special'),
    url(r'^Menu/',include('Menu.urls')),
    url(r'^logout/$', views.user_logout, name='logout'),
    url('^', include('django.contrib.auth.urls')),



    ## path('<int:pk>/', DetailView.as_view(template_name="Menu/bj.html")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)