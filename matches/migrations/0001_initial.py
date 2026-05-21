import uuid
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
            name='MatchData',
            fields=[
                ('id_match', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=100)),
                ('surface', models.CharField(max_length=50)),
                ('best_of', models.IntegerField(choices=[(1, '1'), (3, '3'), (5, '5')])),
                ('match_state', models.CharField(
                    choices=[
                        ('ACEPTADO', 'Aceptado'),
                        ('INICIADO', 'Iniciado'),
                        ('PAUSADO', 'Pausado'),
                        ('FINALIZADA', 'Finalizada'),
                    ],
                    default='ACEPTADO',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player_1', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='player_1_matches',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('player_2', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='player_2_matches',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'match_data'},
        ),
        migrations.CreateModel(
            name='MatchScore',
            fields=[
                ('id_match_score', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('duration', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id_partido', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_score',
                    to='matches.matchdata',
                )),
                ('winner_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_wins',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'match_score'},
        ),
        migrations.CreateModel(
            name='MatchSet',
            fields=[
                ('id_set', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score_p1', models.IntegerField()),
                ('score_p2', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id_match_score', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_sets',
                    to='matches.matchscore',
                )),
                ('winner_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='set_wins',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'match_set'},
        ),
        migrations.CreateModel(
            name='MatchGame',
            fields=[
                ('id_game', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('p1_game_final_score', models.IntegerField()),
                ('p2_game_final_score', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('is_break', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id_set', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_games',
                    to='matches.matchset',
                )),
                ('is_serving', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='games_serving',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('winner_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='game_wins',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'match_game'},
        ),
        migrations.CreateModel(
            name='MatchPoint',
            fields=[
                ('id_point', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score_p1', models.CharField(max_length=5)),
                ('score_p2', models.CharField(max_length=5)),
                ('duration', models.IntegerField()),
                ('break_point_chance', models.BooleanField()),
                ('break_point', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id_game', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_points',
                    to='matches.matchgame',
                )),
                ('id_player_1', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='player_1_points',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('id_player_2', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='player_2_points',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('is_serving', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='points_serving',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('winner_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='point_wins',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'match_point'},
        ),
    ]
