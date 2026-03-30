from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, RecruiterViewSet, CandidateViewSet,workExperienceViewSet

router = DefaultRouter()
router.register('recruiter', RecruiterViewSet, basename='recruiter')
router.register('candidate', CandidateViewSet, basename='candidate')
router.register('work-experience', workExperienceViewSet, basename = 'work-experience')
urlpatterns = [
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('dashboard/', AuthViewSet.as_view({'get': 'dashboard'}), name='dashboard'),
    path('change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='change-password'),

    path('', include(router.urls)),
]
