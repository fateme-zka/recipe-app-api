# Generated by Django 4.0 on 2022-01-15 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_ingredient'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('time_minutes', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('link', models.CharField(blank=True, max_length=255)),
                ('ingredient', models.ManyToManyField(to='main_app.Ingredient')),
                ('tag', models.ManyToManyField(to='main_app.Tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.user')),
            ],
        ),
    ]