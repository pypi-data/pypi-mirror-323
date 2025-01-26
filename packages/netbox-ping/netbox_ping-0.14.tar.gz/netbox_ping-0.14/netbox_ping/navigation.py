from netbox.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_ping:ping_home',
        link_text='Network Tools',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_ping:initialize_plugin',
                title='Initialize Plugin',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
) 