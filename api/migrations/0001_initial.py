# Generated by Django 2.2.3 on 2019-07-24 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commission_plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lower_percentage', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='lo')),
                ('upper_percentage', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='up')),
                ('min_value', models.DecimalField(decimal_places=2, max_digits=19, verbose_name='min')),
            ],
        ),
        migrations.CreateModel(
            name='Sellers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('phone', models.IntegerField()),
                ('age', models.IntegerField()),
                ('email', models.EmailField(max_length=100)),
                ('cpf', models.IntegerField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Commission_plan', verbose_name='plan')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('commission', models.DecimalField(decimal_places=2, max_digits=20)),
                ('sellers_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sellers', verbose_name='sid')),
            ],
        ),
    ]
