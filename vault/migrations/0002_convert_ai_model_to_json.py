import json
from django.db import migrations, models

def convert_to_json_array(apps, schema_editor):
    Prompt = apps.get_model('vault', 'Prompt')
    for prompt in Prompt.objects.all():
        if prompt.ai_model and not prompt.ai_model.startswith('['):
            # Convert single model string to a list containing that model
            prompt.ai_model = json.dumps([prompt.ai_model])
            prompt.save()
        elif not prompt.ai_model:
            # Handle empty strings
            prompt.ai_model = json.dumps([])
            prompt.save()

class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_to_json_array),
        migrations.AlterField(
            model_name='prompt',
            name='ai_model',
            field=models.JSONField(default=list, blank=True, help_text="AI models/tools used (e.g., ['ChatGPT-4', 'Claude'])")
        ),
    ]
