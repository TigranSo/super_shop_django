# Generated by Django 4.2.1 on 2024-04-05 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_remove_payment_image_orderitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type_mis',
            field=models.CharField(choices=[('горячее', 'горячее'), ('лапша', 'лапша'), ('салаты', 'салаты'), ('закуски', 'закуски'), ('напитки ', 'напитки ')], default='горячее', max_length=50, verbose_name='Вид товара'),
        ),
    ]
