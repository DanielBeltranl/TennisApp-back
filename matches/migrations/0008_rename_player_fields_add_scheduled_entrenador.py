from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_alter_matchpoint_winner_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchdata',
            old_name='id_player_creator',
            new_name='id_local_player',
        ),
        migrations.RenameField(
            model_name='matchdata',
            old_name='id_player_invited',
            new_name='id_invited_player',
        ),
        migrations.AddField(
            model_name='matchdata',
            name='scheduled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='matchdata',
            name='id_entrenador',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coached_matches',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
