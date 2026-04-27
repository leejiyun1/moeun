# apps/products/serializers/package.py

from rest_framework import serializers

from apps.products.models import Drink, Package, PackagePolicy


class PackageCreateSerializer(serializers.Serializer):
    """패키지 생성용 시리얼라이저"""

    require_composition = True

    name = serializers.CharField()
    type = serializers.ChoiceField(choices=Package.PackageType.choices, default=Package.PackageType.CURATED)
    policy_id = serializers.IntegerField(required=False, allow_null=True)
    drink_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        min_length=2,
        max_length=5,
        help_text="패키지에 포함할 술 ID 목록 (2~5개)",
    )
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="패키지 구성 목록. 예: [{'drink_id': 1, 'quantity': 2, 'sort_order': 0}]",
    )

    def validate_name(self, value):
        """패키지 이름 유효성 검사"""
        if not value or not value.strip():
            raise serializers.ValidationError("패키지 이름은 필수입니다.")
        return value.strip()

    def validate_drink_ids(self, value):
        """술 ID 목록 유효성 검사"""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("같은 술은 중복 ID 대신 quantity로 표현해야 합니다.")

        existing_drinks = Drink.objects.filter(id__in=value)
        if existing_drinks.count() != len(value):
            raise serializers.ValidationError("존재하지 않는 술이 포함되어 있습니다.")

        return value

    def validate_policy_id(self, value):
        if value is None:
            return value
        if not PackagePolicy.objects.filter(id=value, status=PackagePolicy.Status.ACTIVE).exists():
            raise serializers.ValidationError("존재하지 않거나 비활성 상태인 패키지 정책입니다.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("패키지 구성은 최소 1개 이상이어야 합니다.")

        normalized_items = []
        seen_drink_ids = set()

        for index, item in enumerate(value):
            drink_id = item.get("drink_id")
            quantity = item.get("quantity", 1)
            sort_order = item.get("sort_order", index)

            if not isinstance(drink_id, int):
                raise serializers.ValidationError("drink_id는 정수여야 합니다.")
            if not isinstance(quantity, int) or quantity < 1:
                raise serializers.ValidationError("quantity는 1 이상의 정수여야 합니다.")
            if not isinstance(sort_order, int) or sort_order < 0:
                raise serializers.ValidationError("sort_order는 0 이상의 정수여야 합니다.")
            if drink_id in seen_drink_ids:
                raise serializers.ValidationError("같은 술은 한 번만 보내고 quantity를 증가시켜야 합니다.")

            seen_drink_ids.add(drink_id)
            normalized_items.append(
                {
                    "drink_id": drink_id,
                    "quantity": quantity,
                    "sort_order": sort_order,
                }
            )

        existing_count = Drink.objects.filter(id__in=seen_drink_ids).count()
        if existing_count != len(seen_drink_ids):
            raise serializers.ValidationError("존재하지 않는 술이 포함되어 있습니다.")

        return normalized_items

    def validate(self, attrs):
        has_drink_ids = "drink_ids" in attrs
        has_items = "items" in attrs

        if has_drink_ids and has_items:
            raise serializers.ValidationError({"items": "drink_ids와 items는 동시에 사용할 수 없습니다."})
        if self.require_composition and not has_drink_ids and not has_items:
            raise serializers.ValidationError({"items": "패키지 구성은 필수입니다."})

        if has_drink_ids:
            attrs["items"] = [
                {"drink_id": drink_id, "quantity": 1, "sort_order": index}
                for index, drink_id in enumerate(attrs.pop("drink_ids"))
            ]

        self._validate_policy_constraints(attrs)
        return attrs

    def _validate_policy_constraints(self, attrs):
        items = attrs.get("items")
        if not items:
            return

        policy = self._get_policy(attrs)
        if not policy:
            total_quantity = sum(item["quantity"] for item in items)
            if not 2 <= total_quantity <= 5:
                raise serializers.ValidationError({"items": "패키지 총 구성 수량은 2~5개여야 합니다."})
            if any(item["quantity"] > 1 for item in items):
                raise serializers.ValidationError({"items": "중복 수량은 패키지 정책이 있을 때만 사용할 수 있습니다."})
            return

        total_quantity = sum(item["quantity"] for item in items)
        if not policy.min_items <= total_quantity <= policy.max_items:
            raise serializers.ValidationError(
                {"items": f"패키지 총 구성 수량은 {policy.min_items}~{policy.max_items}개여야 합니다."}
            )
        if not policy.allow_duplicate_items and any(item["quantity"] > 1 for item in items):
            raise serializers.ValidationError({"items": "이 패키지 정책은 같은 술 중복 구성을 허용하지 않습니다."})

    def _get_policy(self, attrs):
        policy_id = attrs.get("policy_id")
        if policy_id:
            return PackagePolicy.objects.get(id=policy_id)
        if self.instance:
            return self.instance.policy
        return None


class PackageUpdateSerializer(PackageCreateSerializer):
    """패키지 수정용 request serializer."""

    require_composition = False

    name = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=Package.PackageType.choices, required=False)
    policy_id = serializers.IntegerField(required=False, allow_null=True)
    drink_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5,
        required=False,
        help_text="패키지에 포함할 술 ID 목록 (2~5개)",
    )
