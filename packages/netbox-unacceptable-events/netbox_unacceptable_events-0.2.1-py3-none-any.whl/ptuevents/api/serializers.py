from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import PTUEventRelation, PTUEvent, PTUEventAssignment, PTAppSystem, PTAppSystemAssignment, PTUsers, PTWorkstations, PTWorkstationsAssignment
# from django.contrib.auth.models import ContentType
from core.models import ObjectType
from drf_yasg.utils import swagger_serializer_method
from netbox.api.fields import ChoiceField, ContentTypeField
from utilities.api import get_serializer_for_model


class PTUEventSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptuevent-detail'
    )

    class Meta:
        model = PTUEvent
        fields = ('id', 'url', 'display', 'name', 'description')
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PTUEventRelationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptueventrelation-detail'
    )

    class Meta:
        model = PTUEventRelation
        fields = ('id', 'url', 'display', 'name', 'description')
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PTUEventAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptueventassignment-detail')
    object_type = ContentTypeField(
        queryset=ObjectType.objects.all()
    )
    object = serializers.SerializerMethodField(read_only=True)
    ptuevent = PTUEventSerializer(nested=True)
    relation = PTUEventRelationSerializer(
        nested=True, required=False, allow_null=True)

    class Meta:
        model = PTUEventAssignment
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'ptuevent', 'relation', 'created',
            'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'ptuevent', 'relation']

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_object(self, instance):
        serializer = get_serializer_for_model(
            instance.object_type.model_class())
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data


class PTAppSystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptappsystem-detail')

    class Meta:
        model = PTAppSystem
        fields = ('id', 'slug', 'url', 'display', 'name', "description",
                  'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'tenant')
        brief_fields = ('id', 'slug', 'url', 'display', 'name', 'tenant')


class PTAppSystemAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptappsystemassignment-detail')
    object_type = ContentTypeField(
        queryset=ObjectType.objects.all()
    )
    object = serializers.SerializerMethodField(read_only=True)
    app_system = PTAppSystemSerializer(nested=True)

    class Meta:
        model = PTAppSystemAssignment
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'app_system', 'created',
            'last_updated',
        ]
        brief_fields = ['id', 'url', 'display', 'PTAppSystem', 'relation']

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_object(self, instance):
        serializer = get_serializer_for_model(
            instance.object_type.model_class())
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data


class PTUsersSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptusers-detail'
    )

    class Meta:
        model = PTUsers
        fields = ('id', 'url', 'display', 'name', 'description',
                  'firstname', 'lastname', 'status', 'sAMAccountName',
                  'ad_sid', 'vpnIPaddress', 'ad_description',
                  'position', 'department')
        brief_fields = ('id', 'url', 'display', 'name', 'description',
                  'firstname', 'lastname', 'status', 'sAMAccountName',
                  'ad_sid', 'vpnIPaddress', 'ad_description',
                  'position', 'department')


class PTWorkstationsSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ptuevents-api:ptworkstations-detail'
    )

    class Meta:
        model = PTWorkstations
        fields = ('id', 'url', 'display', 'name', 'description',
                  'CN', 'DistinguishedName', 'ad_sid', 'location', 'ad_description')
        brief_fields = ('id', 'url', 'display', 'name', 'description',
                  'CN', 'DistinguishedName', 'ad_sid', 'location', 'ad_description')


class NestedPTWorkstationsAssignmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
            view_name='plugins-api:ptuevents-api:ptworkstations-detail')

    class Meta:
        model = PTWorkstations
        fields = ('id', 'url', 'display', 'name', 'description',
                  'CN', 'DistinguishedName', 'ad_sid', 'location', 'ad_description')


class PTWorkstationsAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
            view_name='plugins-api:ptuevents-api:ptworkstationsassignment-detail')
    object_type = ContentTypeField(queryset=ObjectType.objects.all())
    object = serializers.SerializerMethodField(read_only=True)
    pt_workstations = NestedPTWorkstationsAssignmentSerializer()

    class Meta:
        model = PTWorkstationsAssignment
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'pt_workstations', 'created', 'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_object(self, instance):
        serializer = get_serializer_for_model(
            instance.object_type.model_class())
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data

