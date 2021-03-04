# Generated by Django 2.2.16 on 2021-03-04 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('unique_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='board_creator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Board_Thread',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('tag', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('open', 'open thread'), ('closed', 'closed thread')], default='open', max_length=10)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='board_name', to='restapi.Board')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_creator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserBoardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('moderator', 'moderator User'), ('member', 'only member User'), ('banned', 'banned User')], default='moderator', max_length=10)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='boards', to='restapi.Board')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Thread_Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=200)),
                ('commented_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_creator', to=settings.AUTH_USER_MODEL)),
                ('thread_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_comment', to='restapi.Board_Thread')),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='users',
            field=models.ManyToManyField(through='restapi.UserBoardMapping', to=settings.AUTH_USER_MODEL),
        ),
    ]
