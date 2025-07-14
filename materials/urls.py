from django.urls import path
from rest_framework.routers import DefaultRouter

from materials.apps import MaterialsConfig
from materials.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonDestroyAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    PaymentsViewSet,
    SubscriptionAPIView,
    SubscriptionCoursesAPIView,
)

app_name = MaterialsConfig.name


router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"payments", PaymentsViewSet, basename="payments")

urlpatterns = [
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lesson/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-detail"),
    path("lesson/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lesson/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("subscriptions/courses/", SubscriptionCoursesAPIView.as_view(), name="subscriptions-list"),
] + router.urls
