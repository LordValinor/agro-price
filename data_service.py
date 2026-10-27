import json
from pathlib import Path

from models import Product


DATA_FILE = Path(__file__).parent / "data.json"


def load_products() -> list[Product]:
    """Загружает и валидирует мок-данные из JSON-файла."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        raw_products = json.load(file)

    return [Product.model_validate(item) for item in raw_products]


def get_product(product_id: int) -> Product | None:
    """Возвращает продукт по идентификатору или None."""
    return next(
        (product for product in load_products() if product.id == product_id),
        None,
    )


def filter_products(
    *,
    region: str | None = None,
    category: str | None = None,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[Product]:
    """Фильтрует продукты по региону, категории, названию и прямой цене."""
    products = load_products()

    if region:
        products = [product for product in products if product.region == region]
    if category:
        products = [product for product in products if product.category == category]
    if name:
        search_name = name.casefold()
        products = [
            product for product in products if search_name in product.name.casefold()
        ]
    if min_price is not None:
        products = [
            product for product in products if product.price_direct >= min_price
        ]
    if max_price is not None:
        products = [
            product for product in products if product.price_direct <= max_price
        ]

    return products


def build_advice(product: Product) -> str:
    """Формирует рекомендацию без LLM — только на основе бизнес-правил."""
    if product.change_week > 5:
        return "Цена растёт, возможно, стоит подождать."
    if product.change_week < -5:
        return "Цена падает, рассмотрите альтернативные каналы."
    return "Стабильная цена."


def get_filter_options() -> tuple[list[str], list[str]]:
    """Возвращает уникальные значения для выпадающих списков интерфейса."""
    products = load_products()
    regions = sorted({product.region for product in products})
    categories = sorted({product.category for product in products})
    return regions, categories
