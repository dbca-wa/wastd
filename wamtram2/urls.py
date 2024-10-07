from django.urls import path
from . import views

app_name = "wamtram2"


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("turtles/", views.TurtleListView.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetailView.as_view(), name="turtle_detail"),
    path("new-data-entry/<int:batch_id>/", views.TrtDataEntryFormView.as_view(), name="newtrtdataentry"),
    path("new-data-entry/<int:batch_id>/<int:turtle_id>/", views.TrtDataEntryFormView.as_view(), name="existingtrtdataentry"),
    path("data-entry/<int:entry_id>/", views.TrtDataEntryFormView.as_view(), name="trtdataentry"),
    path("find-tagged-turtle/<int:batch_id>/", views.FindTurtleView.as_view(), name="find_turtle"),
    path("entry-batches/", views.EntryBatchesListView.as_view(), name="entry_batches"),
    path("entry-batches/<int:batch_id>/", views.EntryBatchDetailView.as_view(), name="entry_batch_detail"),
    path("delete-entry/<int:pk>/<int:batch_id>/", views.DeleteEntryView.as_view(), name="delete_entry"),
    path("new-entry-batch/", views.EntryBatchDetailView.as_view(), name="new_batch_detail"),
    path("delete-batch/<int:batch_id>/", views.DeleteBatchView.as_view(), name="delete_batch"),
    path("validate-data-entry-batch/<int:batch_id>/", views.ValidateDataEntryBatchView.as_view(), name="validate_data_entry_batch"),
    path("process-data-entry-batch/<int:batch_id>/", views.ProcessDataEntryBatchView.as_view(), name="process_data_entry_batch"),
    path("observations/<int:pk>/", views.ObservationDetailView.as_view(), name="observationdetail"),
    path('validate-tag/', views.ValidateTagView.as_view(), name='validate_tag'),
    path("templates-manage/", views.TemplateManageView.as_view(), name="template_manage"),
    path("templates-manage/<str:template_key>/", views.TemplateManageView.as_view(), name="template_manage_key"),
    path('templates-manage/get-places/', views.TemplateManageView.as_view(), name='get_template_places'),
    path('search-persons/', views.search_persons, name='search-persons'),
    path('search-places/', views.search_places, name='search-places'),
    path('export/', views.ExportDataView.as_view(), name='export_data'),
    path('export/form/', views.FilterFormView.as_view(), name='export_form'),
    path('dud-tag-manage/', views.DudTagManageView.as_view(), name='dud_tag_manage'),
    path('batches-curation/', views.BatchesCurationView.as_view(), name='batches_curation'),
    path('create-new-entry/', views.CreateNewEntryView.as_view(), name='create_new_entry'),
    path('quick-add-batch/', views.quick_add_batch, name='quick_add_batch'),
    path('batch_code_manage/', views.BatchCodeManageView.as_view(), name='batch_code_manage'),
    path('batch_code_manage/<int:batch_id>/', views.BatchCodeManageView.as_view(), name='add_batches_code'),
    path('get-places/', views.get_places, name='get_places'),
    path('check_batch_code/', views.BatchCodeManageView.as_view(), name='check_batch_code'),
    path('get_place_full_name/', views.get_place_full_name, name='get_place_full_name'),
    path('check_template_name/', views.check_template_name, name='check_template_name'),
    path('search-templates/', views.search_templates, name='search_templates'),
]
