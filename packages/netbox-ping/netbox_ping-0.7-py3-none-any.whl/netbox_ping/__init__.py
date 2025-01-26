from netbox.plugins import PluginConfig

class Config(PluginConfig):
    name = 'netbox_ping'
    verbose_name = 'NetBox Ping'
    description = 'Ping IPs and subnets'
    version = '0.7'
    author = 'Christian Rose'
    
    # Required settings
    base_url = 'netbox-ping'
    
    # Optional settings with defaults
    default_settings = {
        'coming_soon': True
    }

    # Database models
    django_apps = ['netbox_ping']

config = Config