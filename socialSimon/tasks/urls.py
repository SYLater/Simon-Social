from django.urls import path
from . import views

urlpatterns = [
  path('task_list/', views.task_list, name='add_task'),
  path('create_task/', views.create_task, name='create_task'),
  path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
  path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
]
