from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_alter_gameroom_board_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameroom',
            name='rematch_requested',
        ),
        migrations.RemoveField(
            model_name='gameroom',
            name='rematch_requested_by',
        ),
    ]
