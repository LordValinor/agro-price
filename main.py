from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from data_service import build_advice, filter_products, get_filter_options, get_product
from models import AdviceResponse, Product


BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Agro Price Monitor API",
    description=(
        "API для сравнения цен на сельскохозяйственную продукцию "
        "по регионам и каналам продаж."
    ),
    version="1.0.0",
)

# Подключаем CSS и другие статические файлы по адресу /static/.
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# CORS подготовлен для локальной разработки будущего отдельного фронтенда.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/v1/products", response_model=list[Product], tags=["products"])
def list_products(
    region: str | None = Query(None, description="Федеральный округ"),
    category: str | None = Query(None, description="Категория продукта"),
    name: str | None = Query(None, description="Поиск по названию продукта"),
    min_price: float | None = Query(None, ge=0, description="Минимальная прямая цена"),
    max_price: float | None = Query(None, ge=0, description="Максимальная прямая цена"),
) -> list[Product]:
    """Возвращает список цен с необязательными фильтрами."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price не может быть больше max_price",
        )

    return filter_products(
        region=region,
        category=category,
        name=name,
        min_price=min_price,
        max_price=max_price,
    )


@app.get("/api/v1/products/{product_id}", response_model=Product, tags=["products"])
def product_details(product_id: int) -> Product:
    """Возвращает подробную информацию о конкретной записи."""
    product = get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product


@app.get(
    "/api/v1/advice/{product_id}",
    response_model=AdviceResponse,
    tags=["advice"],
)
def product_advice(product_id: int) -> AdviceResponse:
    """Возвращает рекомендацию, рассчитанную по изменению цены за неделю."""
    product = get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    return AdviceResponse(
        product_id=product.id,
        recommendation=build_advice(product),
        change_week=product.change_week,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index_page(
    request: Request,
    region: str | None = None,
    category: str | None = None,
    name: str | None = None,
) -> HTMLResponse:
    """Рендерит таблицу цен и форму фильтрации."""
    regions, categories = get_filter_options()
    products = filter_products(region=region, category=category, name=name)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "regions": regions,
            "categories": categories,
            "selected_region": region or "",
            "selected_category": category or "",
            "selected_name": name or "",
        },
    )


@app.get("/product/{product_id}", response_class=HTMLResponse, include_in_schema=False)
def product_page(request: Request, product_id: int) -> HTMLResponse:
    """Рендерит карточку продукта и рекомендацию."""
    product = get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={"product": product, "advice": build_advice(product)},
    )
