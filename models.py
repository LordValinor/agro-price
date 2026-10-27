from datetime import datetime

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Цена сельскохозяйственной продукции в регионе."""

    id: int = Field(..., description="Уникальный идентификатор записи")
    name: str = Field(..., description="Название продукта")
    category: str = Field(..., description="Категория продукта")
    region: str = Field(..., description="Федеральный округ")
    price_buyer: float = Field(
        ..., ge=0, description="Цена при продаже перекупщику"
    )
    price_direct: float = Field(
        ..., ge=0, description="Цена при прямой продаже покупателю"
    )
    change_week: float = Field(
        ..., description="Изменение цены за неделю, в процентах"
    )
    updated_at: datetime = Field(..., description="Дата обновления данных")


class AdviceResponse(BaseModel):
    """Рекомендация, сформированная по простым бизнес-правилам."""

    product_id: int = Field(..., description="Идентификатор продукта")
    recommendation: str = Field(..., description="Текст рекомендации")
    change_week: float = Field(..., description="Изменение цены за неделю, %")
