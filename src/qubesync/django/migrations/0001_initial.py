# QuBe Sync's tables: your customers' connections, the runs your app starts, the notifications
# each run's handler has taken, and the QuickBooks ids your app learns, each against its
# connection. Your own tables need nothing. The same tables (columns, keys and indexes) as the
# Rails engine's migration, but for two plain indexes Django keeps to 30-character names.

from django.db import migrations, models
import django.db.models.deletion
import qubesync.django.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('owner_type', models.CharField(max_length=100)),
                ('owner_id', models.CharField(max_length=255)),
                ('qube_id', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('connected', 'connected'), ('setup_cancelled', 'setup_cancelled'), ('stalled', 'stalled')], default='pending', max_length=255)),
                ('stall_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('revision', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'qube_connections',
                'indexes': [
                    models.Index(fields=['owner_type', 'owner_id'], name='qube_connections_owner'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('qube_id',), name='index_qube_connections_on_qube_id'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('operation', models.CharField(max_length=100)),
                ('record_type', models.CharField(max_length=100)),
                ('record_id', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('qube_run_id', models.CharField(blank=True, max_length=255, null=True)),
                ('input', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('revision', models.IntegerField(default=0)),
                ('state', models.CharField(default='starting', max_length=255)),
                ('outcome', models.CharField(blank=True, max_length=255, null=True)),
                ('error', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('cancel_reason', models.TextField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('question', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('links', qubesync.django.fields.JSONTextField(blank=True, null=True)),
                ('run_url', models.CharField(blank=True, max_length=255, null=True)),
                ('cancel_url', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='runs', to='qubesync.connection')),
            ],
            options={
                'db_table': 'qube_runs',
                'indexes': [
                    models.Index(fields=['record_type', 'record_id', 'operation', 'created_at'], name='qube_runs_record_operation'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('reference',), name='index_qube_runs_on_reference'),
                ],
            },
        ),
        migrations.CreateModel(
            name='QuickbooksRecord',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('kind', models.CharField(max_length=100)),
                ('list', models.CharField(max_length=100)),
                ('qb_id', models.CharField(max_length=100)),
                ('edit_sequence', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('record_type', models.CharField(blank=True, max_length=100, null=True)),
                ('record_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.PROTECT, related_name='quickbooks_records', to='qubesync.connection')),
            ],
            options={
                'db_table': 'qube_quickbooks_records',
                'constraints': [
                    models.UniqueConstraint(fields=('connection', 'list', 'qb_id'), name='index_qube_quickbooks_records_on_qb_id'),
                    models.UniqueConstraint(fields=('connection', 'kind', 'record_type', 'record_id'), name='index_qube_quickbooks_records_on_record'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('delivery_id', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='qubesync.run')),
            ],
            options={
                'db_table': 'qube_notifications',
                'constraints': [
                    models.UniqueConstraint(fields=('run', 'delivery_id'), name='index_qube_notifications_on_run_and_delivery'),
                ],
            },
        ),
    ]
