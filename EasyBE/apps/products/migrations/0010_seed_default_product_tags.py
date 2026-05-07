from django.db import migrations

DEFAULT_PRODUCT_TAGS = [
    {
        "name": "선물 적합",
        "slug": "gift-suitable",
        "group": "DISPLAY",
        "description": "선물용 상품 노출과 검색 필터에 사용합니다.",
        "sort_order": 10,
    },
    {
        "name": "수상작",
        "slug": "award-winning",
        "group": "RECOMMENDATION",
        "description": "수상 이력이 있는 상품 노출과 추천 가중치에 사용합니다.",
        "sort_order": 20,
    },
    {
        "name": "지역 특산주",
        "slug": "regional-specialty",
        "group": "DISPLAY",
        "description": "지역 특산주 노출과 검색 필터에 사용합니다.",
        "sort_order": 30,
    },
    {
        "name": "리미티드",
        "slug": "limited-edition",
        "group": "DISPLAY",
        "description": "한정 판매 상품 노출과 검색 필터에 사용합니다.",
        "sort_order": 40,
    },
    {
        "name": "프리미엄",
        "slug": "premium",
        "group": "RECOMMENDATION",
        "description": "프리미엄 상품 노출과 추천 가중치에 사용합니다.",
        "sort_order": 50,
    },
    {
        "name": "유기농",
        "slug": "organic",
        "group": "FEATURE",
        "description": "유기농 상품 특성 표시에 사용합니다.",
        "sort_order": 60,
    },
]


def seed_default_product_tags(apps, schema_editor):
    ProductTag = apps.get_model("products", "ProductTag")
    for tag in DEFAULT_PRODUCT_TAGS:
        ProductTag.objects.update_or_create(slug=tag["slug"], defaults={**tag, "is_active": True})


def remove_default_product_tags(apps, schema_editor):
    ProductTag = apps.get_model("products", "ProductTag")
    ProductTag.objects.filter(slug__in=[tag["slug"] for tag in DEFAULT_PRODUCT_TAGS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0009_remove_product_is_award_winning_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_default_product_tags, remove_default_product_tags),
    ]
