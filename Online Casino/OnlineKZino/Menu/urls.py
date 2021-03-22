from sys import path

from django.conf.urls import url
from django.views.generic import DetailView

from Menu import views
# SET THE NAMESPACE!
from Menu.models import CustomUser

app_name = 'Menu'




# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$',views.register,name='register'),
    url(r'^user_login/$',views.user_login,name='user_login'),

    url(r'top/$', views.TopU, name="TopU"),
    url(r'private/$', views.Cabinet, name="Cabinet"),
    url(r'private/settings/$', views.Settings, name='Settings'),
    url(r'^top/(?P<pk>\d+)/$', DetailView.as_view(model=CustomUser, template_name="Menu/cab.html") ),
    url(r'BJ/$', views.BJ, name="BJ"),
    url(r'BJstart/$', views.BJstart, name="BJstart"),
    url(r'BJend/$', views.BJend, name="BJend"),
    url(r'WJstart/$', views.WJstart, name="WJstart"),
    url(r'PTstart/$', views.PTstart, name="PTstart"),
    url(r'PT/$', views.PT, name="PT"),
    url(r'PTend/$', views.PTend, name="PTend"),
    url(r'RouletteStart/$', views.RouletteStart, name="RouletteStart"),
    url(r'Roulette/$', views.Roulette, name="Roulette"),
    url(r'RouletteEnd/$', views.RouletteEnd, name="RouletteEnd"),
    url(r'bega/$', views.bega, name="bega"),
    url(r'begast/$', views.begaSTART, name="begaSTART"),
    url(r'begast1/$', views.begaSTART1, name="begaSTART1"),
    url(r'Slots_Start/$', views.Slot_Machine_Start, name="Slots_Start"),
    url(r'Slots/$', views.Slot_Machine, name="Slots"),
    url(r'Slots_END/$', views.Slot_Machine_END, name="Slots_END"),
]