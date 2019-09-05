# Generated by Django 2.0.13 on 2019-03-05 10:16

import autoslug.fields
from django.db import migrations


def regenerate_slug(apps, schema_editor):
    visits = apps.get_model('advisornotes', 'AdvisorVisit')
    for visit in visits.objects.all():
        if not visit.slug:
            visit.save()


class Migration(migrations.Migration):

    dependencies = [
        ('advisornotes', '0007_add_new_visit_data_null_autoslug'),
    ]

    operations = [
        migrations.RunPython(regenerate_slug, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='advisorvisit',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True),
            preserve_default=False,
        ),
    ]
