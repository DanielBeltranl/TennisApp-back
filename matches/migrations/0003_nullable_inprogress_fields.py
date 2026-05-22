from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_update_matchdata_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # MatchScore: winner y duration nullable
        migrations.AlterField(
            model_name='matchscore',
            name='winner_id',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='match_wins',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='matchscore',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),

        # MatchSet: winner y duration nullable, score con default 0, agregar updated_at
        migrations.AlterField(
            model_name='matchset',
            name='winner_id',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='set_wins',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='matchset',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matchset',
            name='score_p1',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='matchset',
            name='score_p2',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='matchset',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),

        # MatchGame: winner, duration, scores finales e is_break nullable
        migrations.AlterField(
            model_name='matchgame',
            name='winner_id',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='game_wins',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='matchgame',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matchgame',
            name='p1_game_final_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matchgame',
            name='p2_game_final_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matchgame',
            name='is_break',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
