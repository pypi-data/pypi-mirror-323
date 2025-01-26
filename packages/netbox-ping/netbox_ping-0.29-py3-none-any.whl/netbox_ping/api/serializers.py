from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import PluginSettingsModel

class PluginSettingsModelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_ping:pluginsettingsmodel-detail'
    )

    class Meta:
        model = PluginSettingsModel
        fields = (
            'id', 'url', 'display', 'update_tags', 'custom_field_data', 'created', 'last_updated'
        )
        brief_fields = ['id', 'url', 'update_tags'] 