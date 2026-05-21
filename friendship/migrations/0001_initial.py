import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[('PENDIENTE', 'Pendiente'), ('ACEPTADO', 'Aceptado')],
                    default='PENDIENTE',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='friendships_initiated',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('friend', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='friendships_received',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'friendship',
                'unique_together': {('user', 'friend')},
            },
        ),
    ]
