from dataclasses import dataclass, field

PRICE_FIELD_NAMES = (
    "freemiumGoldPrice",
    "premiumGoldPrice",
    "freemiumCoinPrice",
    "premiumCoinPrice",
    "baseFreemiumSellPrice",
    "basePremiumSellPrice",
)

WEAPON_TYPES = {"sword", "hammer", "spear", "staff", "dagger", "axe"}
OUTPUT_ORDER = ("armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe")


@dataclass(frozen=True)
class ItemRecord:
    item_type: str
    data: dict = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, item_type, mapping):
        return cls(item_type=item_type, data=dict(mapping))

    def as_dict(self):
        return dict(self.data)

    def sort_key(self):
        if self.item_type == "armor":
            return (self.data.get("maxLevelArmor", self.data.get("armor", 0)), self.data.get("name", ""))
        if self.item_type == "ring":
            return (self.data.get("armor", 0), self.data.get("name", ""))
        if self.item_type in WEAPON_TYPES:
            return (self.data.get("maxLevelDamage", self.data.get("damage", 0)), self.data.get("name", ""))
        return (self.data.get("name", ""),)


@dataclass(frozen=True)
class ClassRecord:
    data: dict = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping):
        return cls(data=dict(mapping))

    def as_dict(self):
        return dict(self.data)


@dataclass(frozen=True)
class EnemyRecord:
    data: dict = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping):
        return cls(data=dict(mapping))

    def as_dict(self):
        return dict(self.data)


def record_to_mapping(value):
    if hasattr(value, "as_dict"):
        return value.as_dict()
    return dict(value)
