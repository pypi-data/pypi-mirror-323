from django.contrib.contenttypes.models import ContentType
from extras.models import CustomField, Tag, CustomLink
from ipam.models import IPAddress, Prefix
from core.models import ObjectType
from extras.choices import CustomFieldTypeChoices
from django.db import IntegrityError

def initialize_plugin():
    """Initialize plugin settings."""
    
    # Create required tags
    tags_to_create = [
        {
            'name': 'online',
            'description': 'Device is online',
            'color': '4CAF50'  # Green
        },
        {
            'name': 'offline',
            'description': 'Device is offline',
            'color': 'F44336'  # Red
        },
        {
            'name': 'auto-discovered',
            'description': 'IP was automatically discovered',
            'color': '2196F3'  # Blue
        }
    ]
    
    for tag_data in tags_to_create:
        Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults={
                'description': tag_data['description'],
                'color': tag_data['color']
            }
        )
    
    # Get the content types we need
    ipaddress_ct = ContentType.objects.get(app_label='ipam', model='ipaddress')
    prefix_ct = ContentType.objects.get(app_label='ipam', model='prefix')
    
    # Get ObjectType instances
    ipaddress_type = ObjectType.objects.get(app_label='ipam', model='ipaddress')
    prefix_type = ObjectType.objects.get(app_label='ipam', model='prefix')
    
    # Define custom links data
    custom_links_data = [
        {
            'name': 'Ping IP',
            'link_text': 'Ping',
            'link_url': '{% url "plugins:netbox_ping:ping_ip" object.address %}',
            'weight': 100,
            'object_types': [ipaddress_type]
        },
        {
            'name': 'Ping Subnet',
            'link_text': 'Ping Subnet',
            'link_url': '{% url "plugins:netbox_ping:scan_prefix" object.prefix %}?action=ping',
            'weight': 100,
            'object_types': [prefix_type]
        },
        {
            'name': 'Discover IPs',
            'link_text': 'Discover IPs',
            'link_url': '{% url "plugins:netbox_ping:scan_prefix" object.prefix %}?action=scan',
            'weight': 200,
            'object_types': [prefix_type]
        }
    ]

    # Create or update custom links
    for link_data in custom_links_data:
        object_type = link_data.pop('object_types', [])
        link, created = CustomLink.objects.get_or_create(
            name=link_data['name'],
            defaults=link_data
        )
        if created:
            print(f"Created custom link: {link.name}")
        # Ensure the object type is associated
        for ct in object_type:
            if not link.object_types.filter(id=ct.id).exists():
                link.object_types.add(ct)
                print(f"Associated {ct} with custom link: {link.name}")
    
    # Define custom fields
    custom_fields_data = [
        {
            'name': 'Up_Down',
            'type': CustomFieldTypeChoices.TYPE_BOOLEAN,
            'label': 'Up/Down Status',
            'description': 'Current up/down status of the IP',
            'object_types': [ipaddress_ct]
        },
        {
            'name': 'dns_name',
            'type': CustomFieldTypeChoices.TYPE_TEXT,
            'label': 'DNS Name',
            'description': 'Resolved DNS name for this IP',
            'object_types': [ipaddress_ct]
        },
        {
            'name': 'Auto_discovered',
            'type': CustomFieldTypeChoices.TYPE_DATE,  # Assuming 'date' maps to TYPE_DATE
            'label': 'Auto Discovered',
            'description': 'Date when this IP was automatically discovered',
            'required': False,
            'filter_logic': 'exact',
            'ui_visible': 'always',
            'ui_editable': 'yes',
            'is_cloneable': True,
            'weight': 101,
            'object_types': [ipaddress_ct]
        },
        {
            'name': 'Last_Seen',
            'type': CustomFieldTypeChoices.TYPE_TEXT,  # Change to TEXT type
            'label': 'Last Seen',
            'description': 'Last time this IP responded to ping',
            'required': False,
            'object_types': [ipaddress_ct]
        }
    ]
    
    # Create or update custom fields
    for cf_data in custom_fields_data:
        object_types = cf_data.pop('object_types', [])
        defaults = cf_data.copy()
        name = defaults.pop('name')
        try:
            custom_field, created = CustomField.objects.get_or_create(
                name=name,
                defaults=defaults
            )
            if created:
                print(f"Created custom field: {custom_field.name}")
            # Update existing fields with any new defaults if necessary
            else:
                updated = False
                for key, value in defaults.items():
                    if getattr(custom_field, key) != value:
                        setattr(custom_field, key, value)
                        updated = True
                if updated:
                    custom_field.save()
                    print(f"Updated custom field: {custom_field.name}")
            # Associate object types
            for ct in object_types:
                if not custom_field.object_types.filter(id=ct.id).exists():
                    custom_field.object_types.add(ct)
                    print(f"Associated {ct} with custom field: {custom_field.name}")
        except Exception as e:
            print(f"Failed to create or update custom field '{name}': {str(e)}")

    # Create Last_Seen custom field
    last_seen_field, _ = CustomField.objects.get_or_create(
        name='Last_Seen',
        defaults={
            'type': CustomFieldTypeChoices.TYPE_TEXT,  # Change to TEXT type
            'label': 'Last Seen',
            'description': 'Last time this IP responded to ping',
            'required': False,
            'object_types': [ipaddress_ct]
        }
    )

    # Update existing field if needed
    if last_seen_field.type != CustomFieldTypeChoices.TYPE_TEXT:
        last_seen_field.type = CustomFieldTypeChoices.TYPE_TEXT
        last_seen_field.save()
