import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import PTUEvent, PTUEventRelation, PTUEventAssignment, PTAppSystem, PTAppSystemAssignment, PTWorkstations, PTUsers


class PTUEventTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    # default_action = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = PTUEvent
        fields = ('pk', 'name', 'description')
        default_columns = ('name', 'description')


class PTUEventRelationTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PTUEventRelation
        fields = ('pk', 'name', 'description')
        default_columns = ('name', 'description')


class PTUEventAssignmentTable(NetBoxTable):
    object_type = columns.ContentTypeColumn(
        verbose_name='Object Type'
    )
    object = tables.Column(
        linkify=True,
        orderable=False
    )
    PTUEvent = tables.Column(
        linkify=True
    )
    relation = tables.Column(
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )

    class Meta(NetBoxTable.Meta):
        model = PTUEventAssignment
        fields = ('pk', 'object_type', 'object',
                  'ptuevent', 'relation', 'actions')
        default_columns = ('pk', 'object_type', 'object',
                           'ptuevent', 'relation')


class AppSystemTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PTAppSystem
        fields = ('pk', 'id', 'name', 'tenant', 'description', 'comments')
        default_columns = ('name', 'description')


class AppSystemAssignmentTable(NetBoxTable):
    object_type = columns.ContentTypeColumn(verbose_name='Object type')
    object = tables.Column(linkify=True, orderable=False)
    app_system = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = PTAppSystemAssignment
        fields = ('pk', 'object_type', 'object', 'app_system', 'actions')
        default_columns = ('pk', 'object_type', 'object', 'app_system')


class PTUsersTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = PTUsers
        fields = ('pk', 'name', 'sAMAccountName',
                  'status',
                  'firstname',
                  'lastname', 'ad_sid', 'ad_description', 'position', 'department', 'comment',
                  'vpnIPaddress', 'description')
        default_columns = ('name', 'sAMAccountName',
                  'status',
                  'firstname',
                  'lastname', 'ad_sid', 'description')


class PTWorkstationsTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PTWorkstations
        fields = ('pk', 'name', 'CN', 'DistinguishedName', 'location', 'ad_description', 'description')
        default_columns = ('name', 'CN', 'DistinguishedName', 'location', 'ad_description', 'description')


class PTWorkstationsAssignmentTable(NetBoxTable):
    object_type = columns.ContentTypeColumn(verbose_name='Object type')
    object = tables.Column(linkify=True, orderable=False)
    app_system = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = PTAppSystemAssignment
        fields = ('pk', 'object_type', 'object', 'pt_workstations', 'actions')
        default_columns = ('pk', 'object_type', 'object', 'pt_workstations')


