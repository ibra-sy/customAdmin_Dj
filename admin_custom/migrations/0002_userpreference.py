# Generated migration for UserPreference model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_custom', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme_modern', models.CharField(choices=[('bleu-moderne', 'Bleu Moderne'), ('emeraude', 'Émeraude'), ('coucher-soleil', 'Coucher de soleil'), ('sombre', 'Mode sombre')], default='bleu-moderne', help_text="Thème pour l'interface moderne", max_length=50)),
                ('theme_classic', models.CharField(choices=[('default', 'Par défaut'), ('nostalgie', 'Nostalgie'), ('ocean', 'Océan'), ('sunset', 'Coucher de soleil'), ('forest', 'Forêt'), ('dark', 'Sombre'), ('liquid-glass', 'Crystal Glass')], default='default', help_text="Thème pour l'interface classique", max_length=50)),
                ('sidebar_collapsed', models.BooleanField(default=False, help_text='Barre latérale réduite par défaut')),
                ('items_per_page', models.IntegerField(default=25, help_text='Nombre d\'éléments par page')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_preference', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Préférence utilisateur',
                'verbose_name_plural': 'Préférences utilisateur',
            },
        ),
    ]
