from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500

handler404 = 'smurf_web_app.views.error_404' 
handler500 = 'smurf_web_app.views.error_500'

urlpatterns = [
        path('home/', views.landing_page, name='landing_page'),
        #path('set/srigoal/<str:token>', views.set_sri_goal, name='set_sri_goal'),
        path('set/srigoal/<int:building_id>/', views.set_sri_goal, name='set_sri_goal'),
        path('scenarios/', views.upgrade_scenarios, name='upgrade_scenarios'),
        ##path('about/', views.custom_error_404, name='about'),
        path('about/', views.about, name='about'),
        ]

