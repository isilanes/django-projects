# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-12 17:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_name', models.CharField(max_length=200, verbose_name='Name of IP')),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(verbose_name='Starting date')),
                ('end', models.DateTimeField(verbose_name='Ending date')),
                ('quota', models.FloatField(default=0)),
                ('status', models.CharField(default='active', max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('user', models.CharField(max_length=20)),
                ('finished', models.BooleanField(default=False)),
                ('in_buffer', models.BooleanField(default=False)),
                ('cpuh', models.FloatField(default=0.0)),
                ('proj_id', models.CharField(max_length=100)),
                ('ip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.IP')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='reservation', max_length=50, verbose_name='Name of reservation')),
                ('start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Starting date')),
                ('end', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Ending date')),
                ('nodes', models.IntegerField(default=1, verbose_name='Amount of nodes')),
            ],
        ),
        migrations.AddField(
            model_name='period',
            name='proj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project'),
        ),
    ]
