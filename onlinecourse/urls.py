
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "onlinecourse"

urlpatterns = [
    # Course listing page
    path(
        "",
        views.CourseListView.as_view(),
        name="index",
    ),

    # User authentication
    path(
        "registration/",
        views.registration_request,
        name="registration",
    ),
    path(
        "login/",
        views.login_request,
        name="login",
    ),
    path(
        "logout/",
        views.logout_request,
        name="logout",
    ),

    # Course details
    path(
        "course/<int:pk>/",
        views.CourseDetailView.as_view(),
        name="course_details",
    ),

    # Enroll in a course
    path(
        "course/<int:course_id>/enroll/",
        views.enroll,
        name="enroll",
    ),

    # Submit exam answers
    path(
        "course/<int:course_id>/submit/",
        views.submit,
        name="submit",
    ),

    # Display exam results
    path(
        "course/<int:course_id>/submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
