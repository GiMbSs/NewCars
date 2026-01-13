from django.urls import path
from .views import CarListView, CarDetailView, CarCreateView, CarUpdateView, CarDeleteView

urlpatterns = [
    path('', CarListView.as_view(), name='list_cars'),
    path('<int:car_id>/', CarDetailView.as_view(), name='car_detail'),
    path('cadastrar/', CarCreateView.as_view(), name='create_car'),
    path('editar/<int:car_id>/', CarUpdateView.as_view(), name='update_car'),
    path('deletar/<int:car_id>/', CarDeleteView.as_view(), name='delete_car'),
]