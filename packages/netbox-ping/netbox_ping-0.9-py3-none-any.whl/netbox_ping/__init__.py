from netbox.plugins import PluginConfig

class Config(PluginConfig):
    name = 'netbox_ping'
    verbose_name = 'NetBox Ping'
    description = 'Ping IPs and subnets'
    version = '0.9'
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

config = Config