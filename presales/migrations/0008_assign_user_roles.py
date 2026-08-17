from django.db import migrations


PRESALES_USERS = [
    "abanob.boschra@protec-gp.com",
    "basma.nasser@protec-gp.com",
    "fatma.hussein@protec-gp.com",
    "m.ramadan@protec-gp.com",
    "menna.abdelwahab@protec-gp.com",
]

MANAGEMENT_USERS = [
    "hany.kamel@protec-gp.com",
    "m.fawzy@protec-gp.com",
    "sherif.gad@protec-gp.com",
    "ahmed.fawzy@protec-gp.com",
]


def assign_roles(apps, schema_editor):

    Person = apps.get_model("presales", "Person")

    Person.objects.filter(
        email__in=PRESALES_USERS
    ).update(
        role="PRESALES"
    )

    Person.objects.filter(
        email__in=MANAGEMENT_USERS
    ).update(
        role="MANAGEMENT"
    )


def reverse_roles(apps, schema_editor):

    Person = apps.get_model("presales", "Person")

    Person.objects.filter(
        email__in=PRESALES_USERS
    ).update(
        role="MEMBER"
    )

    Person.objects.filter(
        email__in=MANAGEMENT_USERS
    ).update(
        role="VIEWER"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("presales", "0007_alter_person_role"),
    ]

    operations = [
        migrations.RunPython(
            assign_roles,
            reverse_roles,
        ),
    ]