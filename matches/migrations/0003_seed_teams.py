from django.db import migrations

TEAMS = [
    # UEFA (Europe)
    ('France', 'FR'), ('Spain', 'ES'), ('Germany', 'DE'), ('Portugal', 'PT'),
    ('Netherlands', 'NL'), ('Belgium', 'BE'), ('Italy', 'IT'), ('Croatia', 'HR'),
    ('Switzerland', 'CH'), ('Denmark', 'DK'), ('Poland', 'PL'), ('Austria', 'AT'),
    ('Norway', 'NO'), ('Ukraine', 'UA'), ('Serbia', 'RS'), ('Slovakia', 'SK'),
    ('Sweden', 'SE'),
    # CONMEBOL (South America)
    ('Argentina', 'AR'), ('Brazil', 'BR'), ('Uruguay', 'UY'), ('Colombia', 'CO'),
    ('Ecuador', 'EC'), ('Paraguay', 'PY'),
    # CONCACAF (North/Central America & Caribbean)
    ('Mexico', 'MX'), ('United States', 'US'), ('Canada', 'CA'),
    ('Costa Rica', 'CR'), ('Panama', 'PA'), ('Jamaica', 'JM'),
    # AFC (Asia)
    ('Japan', 'JP'), ('South Korea', 'KR'), ('Iran', 'IR'), ('Saudi Arabia', 'SA'),
    ('Australia', 'AU'), ('Qatar', 'QA'), ('Uzbekistan', 'UZ'), ('Jordan', 'JO'),
    # CAF (Africa)
    ('Morocco', 'MA'), ('Senegal', 'SN'), ('Nigeria', 'NG'), ('Ghana', 'GH'),
    ('Egypt', 'EG'), ('Algeria', 'DZ'), ('Tunisia', 'TN'), ('Cameroon', 'CM'),
    ('Ivory Coast', 'CI'), ('Cape Verde', 'CV'),
    # OFC (Oceania)
    ('New Zealand', 'NZ'),
]


def seed_teams(apps, schema_editor):
    Team = apps.get_model('matches', 'Team')
    for name, code in TEAMS:
        Team.objects.get_or_create(code=code, defaults={'name': name})


def remove_teams(apps, schema_editor):
    Team = apps.get_model('matches', 'Team')
    codes = [code for _, code in TEAMS]
    Team.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_team_remove_fixture_fixture_id_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_teams, remove_teams),
    ]
