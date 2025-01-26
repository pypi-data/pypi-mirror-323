from netbox.plugins import PluginConfig

class Config(PluginConfig):
    name = 'netbox_ping'
    verbose_name = 'NetBox Ping'
    description = 'Ping IPs and subnets'
    version = '0.10'
    author = 'Christian Rose'
    
    # Required settings
    base_url = 'netbox-ping'
    
    # Optional settings with defaults
    default_settings = {
        'coming_soon': True
    }

    # Register the custom table
    ipaddress_table = 'netbox_ping.tables.CustomIPAddressTable'
    
    # Define which models support custom fields
    custom_field_models = ['ipaddress']

    # Register API serializers
    def ready(self):
        from . import signals
        from .api.serializers import PluginSettingsModelSerializer
        self.serializer_classes = {
            'PluginSettingsModel': PluginSettingsModelSerializer,
        }

config = Config