# Generated by Django 5.1 on 2024-11-29 18:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='main.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.productinstance')),
            ],
        ),
        migrations.AddField(
            model_name='productinstance',
            name='product_type_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.producttype'),
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('product_type_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.producttype')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('product_instance_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.productinstance')),
                ('property_type_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.propertytype')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('product_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.productinstance')),
                ('property_instances', models.ManyToManyField(blank=True, to='main.propertyinstance')),
            ],
        ),
        migrations.CreateModel(
            name='ImagesInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='media/')),
                ('image_instance_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.stock')),
            ],
        ),
    ]
