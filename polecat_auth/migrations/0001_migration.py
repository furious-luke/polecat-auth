from polecat.db.migration import migration, operation
from polecat.db import schema
from polecat.db.schema import column


class Migration(migration.Migration):
    dependencies = []
    operations = [
        operation.CreateTable(
            'auth_user',
            columns=[
                column.SerialColumn('id', unique=True, null=False, primary_key=True),
                column.TextColumn('name', unique=False, null=True, primary_key=False),
                column.TextColumn('email', unique=True, null=False, primary_key=False, max_length=255),
                column.PasswordColumn('password', unique=False, null=True, primary_key=False),
                column.TimestampColumn('created', unique=False, null=True, primary_key=False, default=schema.Auto),
                column.TimestampColumn('logged_out', unique=False, null=True, primary_key=False)
            ]
        )
    ]
