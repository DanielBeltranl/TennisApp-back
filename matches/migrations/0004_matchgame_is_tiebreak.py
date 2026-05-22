from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_nullable_inprogress_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchgame',
            name='is_tiebreak',
            field=models.BooleanField(default=False),
        ),
    ]
