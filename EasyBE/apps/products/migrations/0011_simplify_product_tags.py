from django.db import migrations, models


def normalize_product_tags(apps, schema_editor):
    ProductTag = apps.get_model("products", "ProductTag")
    ProductTag.objects.filter(group="RECOMMENDATION").update(group="DISPLAY")
    ProductTag.objects.filter(name="선물 적합").update(description="상품에 선물용 라벨을 표시할 때 사용합니다.")
    ProductTag.objects.filter(name="수상작").update(description="수상 이력이 있는 상품 라벨 표시에 사용합니다.")
    ProductTag.objects.filter(name="지역 특산주").update(description="지역 특산주 상품 라벨 표시에 사용합니다.")
    ProductTag.objects.filter(name="리미티드").update(description="한정 판매 상품 라벨 표시에 사용합니다.")
    ProductTag.objects.filter(name="프리미엄").update(description="프리미엄 상품 라벨 표시에 사용합니다.")


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0010_seed_default_product_tags"),
    ]

    operations = [
        migrations.RunPython(normalize_product_tags, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name="producttag",
            name="product_tag_slug_8a0b27_idx",
        ),
        migrations.RemoveField(
            model_name="producttag",
            name="slug",
        ),
        migrations.AlterField(
            model_name="producttag",
            name="group",
            field=models.CharField(
                choices=[("DISPLAY", "표시"), ("FEATURE", "특성")],
                default="DISPLAY",
                help_text="태그 그룹",
                max_length=20,
            ),
        ),
    ]
