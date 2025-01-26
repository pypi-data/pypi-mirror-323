from netbox.plugins import PluginConfig
from .models import PluginSettingsModel

class Config(PluginConfig):
    name = 'netbox_ping'
    verbose_name = 'NetBox Ping'
    description = 'Ping IPs and subnets'
    version = '0.4'
    author = 'Christian Rose'
    default_settings = {
        'coming_soon': True
    }

    # Register the custom table
    ipaddress_table = 'netbox_ping.tables.CustomIPAddressTable'
    
    # Define which models support custom fields
    custom_field_models = ['ipaddress']

    # Register our models
    django_apps = ['netbox_ping']
    
    # Register our model
    caching_config = {
        'settings': {
            'model': 'netbox_ping.PluginSettingsModel',
            'key': 'netbox_ping.settings',
        }
    }

    # API settings
    base_url = 'netbox-ping'
    default_app_config = 'netbox_ping.apps.NetBoxPingConfig'

config = Config