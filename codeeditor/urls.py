from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.editor, name='editor'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/', views.list_projects, name='list_projects'),
    path('projects/<str:project_id>/files/', views.list_project_files, name='list_project_files'),
    path('projects/<str:project_id>/files/create/', views.create_file, name='create_file'),
    path('projects/<str:project_id>/delete/', views.delete_project, name='delete_project'),
    path('files/<path:file_id>/', views.get_file_content, name='get_file_content'),
    path('files/<path:file_id>/save/', views.save_file, name='save_file'),
    path('files/<path:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<path:file_id>/rename/', views.rename_file, name='rename_file'),
    path('run/', views.run_code, name='run_code'),
]
 