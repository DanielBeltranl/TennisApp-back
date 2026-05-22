from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_matchgame_is_tiebreak'),
    ]

    operations = [
        # match_data: filtrar partidos finalizados por jugador
        migrations.AddIndex(
            model_name='matchdata',
            index=models.Index(
                fields=['id_player_creator', 'match_state'],
                name='match_data_creator_state_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='matchdata',
            index=models.Index(
                fields=['id_player_invited', 'match_state'],
                name='match_data_invited_state_idx',
            ),
        ),
        # match_point: puntos de un game en orden cronológico
        migrations.AddIndex(
            model_name='matchpoint',
            index=models.Index(
                fields=['id_game', 'created_at'],
                name='match_point_game_time_idx',
            ),
        ),
        # match_point: último punto del partido (undo y recovery)
        migrations.AddIndex(
            model_name='matchpoint',
            index=models.Index(
                fields=['created_at'],
                name='match_point_created_at_idx',
            ),
        ),
    ]
