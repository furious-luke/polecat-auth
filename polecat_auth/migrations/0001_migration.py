from polecat.db.migration import migration, operation
from polecat.db import schema
from polecat.db.schema import column, index, policy


class Migration(migration.Migration):
    dependencies = []
    operations = [
        operation.CreateRole('admin', parents=[]),
        operation.CreateRole('user', parents=['admin']),
        operation.CreateRole('default', parents=['user']),
        operation.CreateTable(
            'auth_entity',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True)
            ]
        ),
        operation.CreateTable(
            'auth_user',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True),
                column.TextColumn('name', unique=False, null=True, primary_key=False),
                column.TextColumn('email', unique=True, null=True, primary_key=False, max_length=255),
                column.PasswordColumn('password', unique=False, null=True, primary_key=False),
                column.TimestampColumn('logged_out', unique=False, null=True, primary_key=False),
                column.TimestampColumn('created', unique=False, null=False, primary_key=False, default=schema.Auto),
                column.BoolColumn('anonymous', unique=False, null=False, primary_key=False, default=False),
                column.RelatedColumn('entity', unique=False, null=True, primary_key=False, related_table='auth_entity', related_column='users')
            ],
            policies=[policy.Policy(name='auth_user_entity', expression="auth_user.entity = current_setting('claims.entity_id', TRUE)::int")]
        ),
        operation.CreateTable(
            'auth_organisation',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True),
                column.TextColumn('name', unique=False, null=False, primary_key=False),
                column.RelatedColumn('entity', unique=False, null=True, primary_key=False, related_table='auth_entity', related_column='organisations')
            ],
            policies=[policy.Policy(name='auth_organisation_id', expression="EXISTS ( SELECT 1 FROM auth_membership mem WHERE mem.user = current_setting('claims.user_id', TRUE)::int AND mem.organisation = auth_organisation.id)")]
        ),
        operation.CreateTable(
            'auth_membership',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True),
                column.RelatedColumn('user', unique=False, null=False, primary_key=False, related_table='auth_user', related_column='memberships'),
                column.RelatedColumn('organisation', unique=False, null=False, primary_key=False, related_table='auth_organisation', related_column='memberships'),
                column.TextColumn('role', unique=False, null=True, primary_key=False),
                column.BoolColumn('active', unique=False, null=False, primary_key=False, default=False)
            ],
            uniques=(('user', 'organisation', 'role'),),
            policies=[policy.Policy(name='auth_membership_user', expression="auth_membership.user = current_setting('claims.user_id', TRUE)::int")]
        ),
        operation.CreateTable(
            'auth_apitoken',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True),
                column.TextColumn('purpose', unique=False, null=True, primary_key=False)
            ]
        )
    ]
