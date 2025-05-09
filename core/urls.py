from django.urls import path
from core.views import main_views, upload_views, import_views

urlpatterns = [
    path('', main_views.index, name='index'),

    # Users
    path('users/', main_views.users_list_view, name='users_list'),

    # Print Events
    path('print-events/', main_views.print_events_view, name='print_events'),
    path('print-tree/', main_views.print_tree_view, name='print_tree'),
    path('print-tree/export/', main_views.export_tree_excel_view, name='export_tree_excel'),

    # Upload
    path('upload/', upload_views.upload_view, name='upload'),

    # API Imports
    path('import/users/', import_views.import_users_api_view, name='import_users_api'),
    path('import/print-events/', import_views.import_print_events_api_view, name='import_print_events_api'),
]
