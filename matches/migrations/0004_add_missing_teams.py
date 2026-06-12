from django.db import migrations

# Teams from the final 48-team World Cup field that aren't in the existing
# seed list yet. Added without removing any existing teams.
NEW_TEAMS = [
    ('Bosnia and Herzegovina', 'BA'), ('Czechia', 'CZ'), ('England', 'EN'),
    ('Scotland', 'SC'), ('Türkiye', 'TR'), ('DR Congo', 'CD'),
    ('South Africa', 'ZA'), ('Iraq', 'IQ'), ('Curaçao', 'CW'), ('Haiti', 'HT'),
]


def add_teams(apps, schema_editor):
    Team = apps.get_model('matches', 'Team')
    for name, code in NEW_TEAMS:
        Team.objects.get_or_create(code=code, defaults={'name': name})


def remove_teams(apps, schema_editor):
    Team = apps.get_model('matches', 'Team')
    Team.objects.filter(code__in=[code for _, code in NEW_TEAMS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_seed_teams'),
    ]

    operations = [
        migrations.RunPython(add_teams, remove_teams),
    ]
