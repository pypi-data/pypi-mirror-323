from netbox.views import generic
from . import forms, models, tables
from django.contrib.contenttypes.models import ContentType
from core.models import ObjectType
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import PTWorkstationsAssignment
from . import filtersets


class PTUEventView(generic.ObjectView):
    queryset = models.PTUEvent.objects.all()


class PTUEventListView(generic.ObjectListView):
    queryset = models.PTUEvent.objects.all()
    table = tables.PTUEventTable
    filterset = filtersets.PTUEventFilterSet
    # actions = ('add', 'export') # old way
    # actions = { # new way (for netbox 4.0)
    #     'add': {'some_permission'},
    #     'export': {'some_permission'}
    # }


class PTUEventEditView(generic.ObjectEditView):
    queryset = models.PTUEvent.objects.all()
    form = forms.PTUEventForm


class PTUEventDeleteView(generic.ObjectDeleteView):
    queryset = models.PTUEvent.objects.all()


# PTPTUEvent relation


class PTUEventRelationView(generic.ObjectView):
    queryset = models.PTUEventRelation.objects.all()


class PTUEventRelationListView(generic.ObjectListView):
    queryset = models.PTUEventRelation.objects.all()
    table = tables.PTUEventRelationTable
    filterset = filtersets.PTUEventRelationFilterSet


class PTUEventRelationEditView(generic.ObjectEditView):
    queryset = models.PTUEventRelation.objects.all()
    form = forms.PTUEventRelationForm


class PTUEventRelationDeleteView(generic.ObjectDeleteView):
    queryset = models.PTUEventRelation.objects.all()


# #
# # PTUEvent assignments
# #

class PTUEventAssignmentEditView(generic.ObjectEditView):
    queryset = models.PTUEventAssignment.objects.all()
    form = forms.PTUEventAssignmentForm
    template_name = 'ptuevents/ptuevent_assignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            object_type = get_object_or_404(
                ContentType, pk=request.GET.get('object_type'))
            instance.object = get_object_or_404(
                object_type.model_class(), pk=request.GET.get('object_id'))
        return instance
    
    def get_extra_addanother_params(self, request):
        return {
            'object_type': request.GET.get('object_type'),
            'object_id': request.GET.get('object_id'),
        }

    def post(self, request, *args, **kwargs):
        form = forms.PTUEventAssignmentForm(request.POST)
        if form.is_valid():
            object_type_id = request.GET.get('object_type', -1)
            object_id = request.GET.get('object_id', -1)
            ptuevent = form.cleaned_data['ptuevent']
            qs = models.PTUEventAssignment.objects.filter(
                object_type=object_type_id, object_id=object_id, ptuevent=ptuevent.id)
            if qs.exists():
                redirect_url = request.GET.get('return_url', '/')
                return HttpResponseRedirect(redirect_url)

        return super().post(request, *args, **kwargs)


class PTUEventAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.PTUEventAssignment.objects.all()


class PTAppSystemView(generic.ObjectView):
    queryset = models.PTAppSystem.objects.all()

    def get_extra_context(self, request, instance):
        print(self)
        print(request)
        print(instance.id)
        app_system_assignments = models.PTAppSystemAssignment.objects.filter(
            app_system=instance)
        assignments_table = tables.AppSystemAssignmentTable(
            app_system_assignments)
        assignments_table.columns.hide('app_system')
        assignments_table.configure(request)
        object_type_id = ObjectType.objects.get_for_model(
            model=models.PTAppSystem).id
        PTUEvent_ass = models.PTUEventAssignment.objects.filter(
            object_id=instance.id, object_type=object_type_id)
        PTUEvents = []
        for r in PTUEvent_ass:
            PTUEvents.append({
                'assignment_id': r.id,
                'name': r.ptuevent,
                'rel': r.relation.name
            })

        return {
            'assignments_table': assignments_table,
            'PTUEvents': PTUEvents
        }


class PTAppSystemListView(generic.ObjectListView):
    queryset = models.PTAppSystem.objects.all()
    table = tables.AppSystemTable
    filterset = filtersets.PTAppSystemFilterSet


class PTAppSystemEditView(generic.ObjectEditView):
    queryset = models.PTAppSystem.objects.all()
    form = forms.PTAppSystemForm


class PTAppSystemDeleteView(generic.ObjectDeleteView):
    queryset = models.PTAppSystem.objects.all()


class PTAppSystemAssignmentEditView(generic.ObjectEditView):
    queryset = models.PTAppSystemAssignment.objects.all()
    form = forms.PTAppSystemAssignmentForm
    template_name = 'ptuevents/appsystem_assignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            object_type = get_object_or_404(
                ContentType, pk=request.GET.get('object_type'))
            instance.object = get_object_or_404(
                object_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_extra_addanother_params(self, request):
        return {
            'object_type': request.GET.get('object_type'),
            'object_id': request.GET.get('object_id'),
        }

    def post(self, request, *args, **kwargs):
        form = forms.PTAppSystemAssignmentForm(request.POST)
        if form.is_valid():
            object_type_id = request.GET.get('object_type', -1)
            object_id = request.GET.get('object_id', -1)
            s = form.cleaned_data['app_system']
            qs = models.PTAppSystemAssignment.objects.filter(
                object_type=object_type_id, object_id=object_id, app_system=s.id)
            if qs.exists():
                redirect_url = request.GET.get('return_url', '/')
                return HttpResponseRedirect(redirect_url)

        return super().post(request, *args, **kwargs)


class PTAppSystemAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.PTAppSystemAssignment.objects.all()


# PTUsers
class PTUsersView(generic.ObjectView):
    queryset = models.PTUsers.objects.all()

    # template_name = 'ptuevents/ptusers.html'

    def get_extra_context(self, request, instance):
        print(self)
        print(request)
        print(instance.id)

        object_type_id = ObjectType.objects.get_for_model(model=models.PTUsers).id
        PTUEvent_ass = models.PTUEventAssignment.objects.filter(object_id=instance.id, object_type=object_type_id)
        PTUEvents = []
        for r in PTUEvent_ass:
            PTUEvents.append({
                'assignment_id': r.id,
                'name'         : r.ptuevent,
                'rel'          : r.relation.name
            })

        pt_workstations = PTWorkstationsAssignment.objects.filter(object_id=instance.id, object_type=object_type_id)
        PTWorkstations = []
        for s in pt_workstations:
            PTWorkstations.append({
                'id'             : s.id,
                'pt_workstations': s.pt_workstations})
            # print(s.__dict__)

        return {
            'PTUEvents'      : PTUEvents,
            'pt_workstations': PTWorkstations
        }


class PTUsersListView(generic.ObjectListView):
    queryset = models.PTUsers.objects.all()
    table = tables.PTUsersTable
    filterset = filtersets.PTUsersFilterSet


class PTUsersEditView(generic.ObjectEditView):
    queryset = models.PTUsers.objects.all()
    form = forms.PTUsersForm


class PTUsersDeleteView(generic.ObjectDeleteView):
    queryset = models.PTUsers.objects.all()

# PTWorkstations


class PTWorkstationsView(generic.ObjectView):
    queryset = models.PTWorkstations.objects.all()
    # template_name = 'ptuevents/ptworkstations.html'

    def get_extra_context(self, request, instance):
        print(self)
        print(request)
        print(instance.id)

        pt_workstations_assignments = models.PTWorkstationsAssignment.objects.filter(pt_workstations=instance)
        pt_workstations_table = tables.PTWorkstationsAssignmentTable(pt_workstations_assignments)
        pt_workstations_table.columns.hide('pt_workstations')
        pt_workstations_table.configure(request)

        object_type_id = ObjectType.objects.get_for_model(
                model=models.PTWorkstations).id
        PTUEvent_ass = models.PTUEventAssignment.objects.filter(
                object_id=instance.id, object_type=object_type_id)
        PTUEvents = []
        for r in PTUEvent_ass:
            PTUEvents.append({
                'assignment_id': r.id,
                'name'         : r.ptuevent,
                'rel'          : r.relation.name
            })

        return {
            'assignments_table': pt_workstations_table,
            'PTUEvents': PTUEvents
        }


class PTWorkstationsListView(generic.ObjectListView):
    queryset = models.PTWorkstations.objects.all()
    table = tables.PTWorkstationsTable
    filterset = filtersets.PTWorkstationsFilterSet


class PTWorkstationsEditView(generic.ObjectEditView):
    queryset = models.PTWorkstations.objects.all()
    form = forms.PTWorkstationsForm


class PTWorkstationsDeleteView(generic.ObjectDeleteView):
    queryset = models.PTWorkstations.objects.all()


class PTWorkstationsAssignmentEditView(generic.ObjectEditView):
    queryset = models.PTWorkstationsAssignment.objects.all()
    form = forms.PTWorkstationsAssignmentForm
    template_name = 'ptuevents/ptworkstations_assignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            object_type = get_object_or_404(
                ContentType, pk=request.GET.get('object_type'))
            instance.object = get_object_or_404(
                object_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_extra_addanother_params(self, request):
        return {
            'object_type': request.GET.get('object_type'),
            'object_id': request.GET.get('object_id'),
        }

    def post(self, request, *args, **kwargs):
        form = forms.PTWorkstationsAssignmentForm(request.POST)
        if form.is_valid():
            object_type_id = request.GET.get('object_type', -1)
            object_id = request.GET.get('object_id', -1)
            s = form.cleaned_data['pt_workstations']
            qs = models.PTWorkstationsAssignment.objects.filter(
                object_type=object_type_id, object_id=object_id, pt_workstations=s.id)
            if qs.exists():
                redirect_url = request.GET.get('return_url', '/')
                return HttpResponseRedirect(redirect_url)

        return super().post(request, *args, **kwargs)


class PTWorkstationsAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.PTWorkstationsAssignment.objects.all()

