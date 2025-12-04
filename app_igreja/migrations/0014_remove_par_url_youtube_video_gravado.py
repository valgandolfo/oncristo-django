# Generated manually to remove PAR_url_youtube_video_gravado field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_igreja', '0013_add_par_url_youtube_video_gravado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tbparoquia',
            name='PAR_url_youtube_video_gravado',
        ),
    ]

