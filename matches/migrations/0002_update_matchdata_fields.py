from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Rename player_1 -> id_player_creator
        migrations.RenameField(
            model_name='matchdata',
            old_name='player_1',
            new_name='id_player_creator',
        ),
        # Rename player_2 -> id_player_invited
        migrations.RenameField(
            model_name='matchdata',
            old_name='player_2',
            new_name='id_player_invited',
        ),
        # Add PENDIENTE to match_state choices and change default
        migrations.AlterField(
            model_name='matchdata',
            name='match_state',
            field=models.CharField(
                choices=[
                    ('PENDIENTE', 'PENDIENTE'),
                    ('ACEPTADO', 'ACEPTADO'),
                    ('INICIADO', 'INICIADO'),
                    ('PAUSADO', 'PAUSADO'),
                    ('FINALIZADA', 'FINALIZADA'),
                ],
                default='PENDIENTE',
                max_length=20,
            ),
        ),
        # Add nullable id_match_score FK (circular reference, optimización de queries)
        migrations.AddField(
            model_name='matchdata',
            name='id_match_score',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='match_data_ref',
                to='matches.matchscore',
            ),
        ),
    ]
