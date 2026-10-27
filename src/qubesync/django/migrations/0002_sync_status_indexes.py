# Indexes for SyncStatus and the connection's scopes (in_quickbooks, not_in_quickbooks,
# needing_answer, sending), as the Rails engine's 20261026230000 migration adds.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qubesync', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='run',
            index=models.Index(fields=['connection', 'record_type', 'record_id', 'operation', 'state'], name='qube_runs_connection_state'),
        ),
        migrations.AddIndex(
            model_name='quickbooksrecord',
            index=models.Index(fields=['connection', 'record_type', 'record_id'], name='qube_qb_records_connection'),
        ),
    ]
