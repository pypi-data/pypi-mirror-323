import django_filters
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter
from .models import *
from django.db.models import Q


class PTUEventFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PTUEvent
        fields = ['id', 'name', 'description', 'comments']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class PTUEventRelationFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PTUEventRelation
        fields = ['id', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ) 


class PTUEventAssignmentFilterSet(ChangeLoggedModelFilterSet):
    object_type = ContentTypeFilter()
    ptuevent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PTUEvent.objects.all(),
        label='PTUEvent (ID)',
    )
    relation_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PTUEventRelation.objects.all(),
        label='PTUEvent relation (ID)',
    )
    relation = django_filters.ModelMultipleChoiceFilter(
        field_name='relation__name',
        queryset=PTUEventRelation.objects.all(),
        to_field_name='name',
        label='PTUEvent relation (name)',
    )

    class Meta:
        model = PTUEventAssignment
        fields = ['id', 'object_type_id', 'object_id']


class PTUsersFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PTUsers
        fields = ['id', 'name', 'firstname', 'lastname', 'status', 'sAMAccountName', 
                'ad_sid', 'vpnIPaddress', 'ad_description', 'position', 
                'department', 'comment', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(firstname__icontains=value) |
            Q(lastname__icontains=value) |
            Q(status__icontains=value) |
            Q(sAMAccountName__icontains=value) |
            Q(ad_sid__icontains=value) |
            Q(vpnIPaddress__icontains=value) |
            Q(ad_description__icontains=value) |
            Q(position__icontains=value) |
            Q(department__icontains=value) |
            Q(comment__icontains=value) |
            Q(description__icontains=value)
        ) 

class PTAppSystemFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = PTAppSystem
        fields = ['id', 'name', 'slug', 'tenant', 'description', 'comments']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class PTAppSystemAssignmentFilterSet(ChangeLoggedModelFilterSet):
    object_type = ContentTypeFilter()
    app_system_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PTAppSystem.objects.all(),
        label='PTAppSystem (ID)',
    )

    class Meta:
        model = PTAppSystemAssignment
        fields = ['id', 'object_type_id', 'object_id']


class PTWorkstationsFilterSet(NetBoxModelFilterSet):
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(ad_description__icontains=value) |
            Q(CN__icontains=value) |
            Q(DistinguishedName__icontains=value) |
            Q(ad_sid__icontains=value) |
            Q(ad_description__icontains=value)
        )

    class Meta:
        model = PTWorkstations
        fields = ['id', 'name', 'description', 'ad_description',
                  'CN', 'DistinguishedName', 'location', 'ad_sid', 'ad_description']


class PTWorkstationsAssignmentFilterSet(ChangeLoggedModelFilterSet):
    object_type = ContentTypeFilter()
    pt_workstations_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PTWorkstations.objects.all(),
        label='Workstation (ID)',
    )

    class Meta:
        model = PTWorkstationsAssignment
        fields = ['id', 'object_type_id', 'object_id']
