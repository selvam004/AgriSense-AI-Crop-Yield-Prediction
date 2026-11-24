from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    # Direct Flask-compatible paths
    path('predict', views.predict_view, name='predict_direct'),
    path('insights', views.insights_view, name='insights_direct'),
    # RESTful API paths
    path('api/predict/', views.predict_view, name='api_predict'),
    path('api/insights/', views.insights_view, name='api_insights'),
    path('api/history/', views.history_view, name='api_history'),
]
