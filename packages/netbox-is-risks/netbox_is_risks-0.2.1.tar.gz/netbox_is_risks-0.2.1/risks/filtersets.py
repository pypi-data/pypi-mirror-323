import django_filters
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter
from .models import *
from django.db.models import Q


class RiskAssignmentFilterSet(ChangeLoggedModelFilterSet):
    object_type = ContentTypeFilter()
    risk_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Risk.objects.all(),
        label='Risk (ID)',
    )
    relation_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RiskRelation.objects.all(),
        label='Risk relation (ID)',
    )
    relation = django_filters.ModelMultipleChoiceFilter(
        field_name='relation__name',
        queryset=RiskRelation.objects.all(),
        to_field_name='name',
        label='Risk relation (name)',
    )

    class Meta:
        model = RiskAssignment
        fields = ['id', 'object_type_id', 'object_id']

class RiskFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Risk
        fields = ['id', 'name', 'description', 'comments']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )

class RiskRelationFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = RiskRelation
        fields = ['id', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ) 
