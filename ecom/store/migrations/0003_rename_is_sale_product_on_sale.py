# Generated by Django 4.2.7 on 2023-11-14 03:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_category_options_product_is_sale_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='is_sale',
            new_name='on_sale',
        ),
    ]