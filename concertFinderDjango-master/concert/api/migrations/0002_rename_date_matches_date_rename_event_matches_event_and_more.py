# Generated by Django 4.1.1 on 2022-09-27 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matches',
            old_name='date',
            new_name='Date',
        ),
        migrations.RenameField(
            model_name='matches',
            old_name='event',
            new_name='Event',
        ),
        migrations.RenameField(
            model_name='matches',
            old_name='likedArtists',
            new_name='LikedArtists',
        ),
        migrations.RenameField(
            model_name='matches',
            old_name='picLink',
            new_name='Link',
        ),
        migrations.RenameField(
            model_name='matches',
            old_name='venue',
            new_name='Venue',
        ),
        migrations.AddField(
            model_name='matches',
            name='img_url',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='matches',
            name='song_url',
            field=models.CharField(default='', max_length=255),
        ),
    ]
