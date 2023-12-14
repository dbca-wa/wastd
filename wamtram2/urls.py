from django.urls import path
from . import views

app_name = "wamtram2"


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("turtles/", views.TurtleListView.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetailView.as_view(), name="turtle_detail"),
    path('newdataentry/<int:batch_id>/', views.TrtDataEntryForm.as_view(), name='newtrtdataentry'),
    path('newdataentry/<int:batch_id>/<int:turtle_id>/', views.TrtDataEntryForm.as_view(), name='existingtrtdataentry'),
    path('dataentry/<int:entry_id>/', views.TrtDataEntryForm.as_view(), name='trtdataentry'),
    path('findTaggedTurtle/<int:batch_id>/', views.FindTurtleView.as_view(), name='find_turtle'),
    path('entryBatches/',views.EntryBatchesListView.as_view(), name='entry_batches'),
    path('entryBatches/<int:batch_id>/',views.EntryBatchDetailView.as_view(), name='entry_batch_detail'),
    path('newEntryBatch/',views.EntryBatchDetailView.as_view(), name='new_batch_detail'),
    path('deleteBatch/<int:batch_id>/', views.DeleteBatchView.as_view(), name='delete_batch'),
    path('validate_data_entry_batch/<int:batch_id>/', views.ValidateDataEntryBatchView.as_view(), name='validate_data_entry_batch'),
    path('process_data_entry_batch/<int:batch_id>/', views.ProcessDataEntryBatchView.as_view(), name='process_data_entry_batch'),
    path('observations/<int:pk>/', views.ObservationDetailView.as_view(), name='observationdetail'),
]
