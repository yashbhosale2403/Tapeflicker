from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_hub, name="hub"),
    path("course/<int:course_id>/", views.course_chat_room, name="course_room"),
    path("course/<int:course_id>/upload/", views.upload_attachment, name="upload_attachment"),
    path("report/<int:message_id>/", views.report_message, name="report_message"),
]
