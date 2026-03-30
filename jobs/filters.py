import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name="salary", lookup_expr='gte')
    max_salary = django_filters.NumberFilter(field_name="salary", lookup_expr='lte')
    company = django_filters.CharFilter(field_name="recruiter__organisation_name", lookup_expr='icontains')
    location = django_filters.CharFilter(field_name="location", lookup_expr='icontains')

    class Meta:
        model = Job
        fields = ['job_type', 'experience_required', 'is_active']
