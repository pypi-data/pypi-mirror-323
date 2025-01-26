from netbox.plugins import PluginConfig

class Config(PluginConfig):
    name = 'netbox_ping'
    verbose_name = 'NetBox Ping'
    description = 'Ping IPs and subnets'
    version = '0.26'
    author = 'Christian Rose'
    default_settings = {
        'coming_soon': True
    }

    # Register the custom table
    ipaddress_table = 'netbox_ping.tables.CustomIPAddressTable'
    
    # Define which models support custom fields
    custom_field_models = ['ipaddress']

    # API settings
    base_url = 'netbox-ping'

    # Register API serializers
    def ready(self):
        from .api.serializers import PluginSettingsModelSerializer
        self.serializer_classes = {
            'PluginSettingsModel': PluginSettingsModelSerializer,
        }

config = Config