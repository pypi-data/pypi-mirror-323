from netbox.plugins import PluginConfig


class NetBoxPTUEventsConfig(PluginConfig):
    name = 'ptuevents'
    verbose_name = 'Unacceptable events and users and computers'
    description = 'Add events related fields to devices and virtual machines, adds application systems'
    version = '0.2.0'
    base_url = 'ptuevents'
    author = 'Artur Shamsiev'
    author_email = 'me@z-lab.me'


config = NetBoxPTUEventsConfig
