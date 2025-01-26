from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import PluginSettingsModel

class PluginSettingsModelSerializer(NetBoxModelSerializer):
    class Meta:
        model = PluginSettingsModel
        fields = ('id', 'update_tags', 'created', 'last_updated') 