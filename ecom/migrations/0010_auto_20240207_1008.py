# Generated by Django 3.0.5 on 2024-02-07 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0009_auto_20240206_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cartlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=20)),
                ('product_id', models.CharField(max_length=20)),
                ('quantity', models.CharField(max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('finalprice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.DeleteModel(
            name='Cartable',
        ),
    ]
