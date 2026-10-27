# qube_sync_marks (when each connection's last completed run of a workflow started) and the plain
# v2 requests your app queues (qube_requests) with the deliveries each has taken
# (qube_request_deliveries), as the Rails engine's 20261027000000 and 20261028000000 migrations.

from django.db import migrations, models
import django.db.models.deletion
import qubesync.django.fields


class Migration(migrations.Migration):

    dependencies = [
        ('qubesync', '0002_sync_status_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncMark',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('workflow', models.CharField(max_length=100)),
                ('started_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='sync_marks', to='qubesync.connection')),
            ],
            options={
                'db_table': 'qube_sync_marks',
                'constraints': [
                    models.UniqueConstraint(fields=('connection', 'workflow'), name='index_qube_sync_marks_on_connection_and_workflow'),
                ],
            },
        ),
        migrations.CreateModel(
            name='QueuedRequest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('operation', models.CharField(max_length=100)),
                ('record_type', models.CharField(max_length=100)),
                ('record_id', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('qube_id', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(default='queued', max_length=50)),
                ('params', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('error', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('pages_answered', models.IntegerField(default=0)),
                ('last_page', models.IntegerField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.PROTECT, related_name='queued_requests', to='qubesync.connection')),
            ],
            options={
                'db_table': 'qube_requests',
                'indexes': [
                    models.Index(fields=['connection', 'record_type', 'record_id', 'operation', 'created_at'], name='qube_requests_record'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('reference',), name='index_qube_requests_on_reference'),
                ],
            },
        ),
        migrations.CreateModel(
            name='RequestDelivery',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dedupe_key', models.CharField(max_length=200)),
                ('page', models.IntegerField(blank=True, null=True)),
                ('state', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='qubesync.queuedrequest')),
            ],
            options={
                'db_table': 'qube_request_deliveries',
                'constraints': [
                    models.UniqueConstraint(fields=('request', 'dedupe_key'), name='index_qube_request_deliveries_on_request_and_key'),
                ],
            },
        ),
    ]
