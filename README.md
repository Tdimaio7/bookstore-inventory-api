# Bookstore Inventory API
API REST para gestionar inventario de libros y calcular precios locales con tipos de cambio en tiempo real.

## Requisitos
- Python 3.11+ o Docker
- Dependencias: ver `requeriments.txt`

## Variables de entorno
Configura `.env`:
- DJANGO_SECRET_KEY
- CURRENCY_DEFAULT (por defecto EUR)
- EXCHANGE_RATE_FALLBACK (por defecto 1.0)

## Ejecutar con Docker
```bash
docker compose up --build
```
La API queda en http://localhost:8000

## Ejecutar local (sin Docker)
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requeriments.txt
python manage.py migrate
python manage.py runserver
```

## Endpoints
- POST /books
- GET /books
- GET /books/{id}
- PUT /books/{id}
- DELETE /books/{id}
- GET /books/search?category={category}
- GET /books/low-stock?threshold=10
- POST /books/{id}/calculate-price

## Cálculo de precio
- Toma `cost_usd`
- Obtiene tasa USD -> moneda local desde https://api.exchangerate-api.com/v4/latest/USD
- Aplica margen 40%
- Actualiza `selling_price_local`
- Retorna detalle del cálculo

## Ejemplo de respuesta calculate-price
```json
{
  "book_id": 1,
  "cost_usd": 15.99,
  "exchange_rate": 0.85,
  "cost_local": 13.59,
  "margin_percentage": 40,
  "selling_price_local": 19.03,
  "currency": "EUR",
  "calculation_timestamp": "2025-01-15T10:30:00Z"
}
```

## Reglas de negocio
- `cost_usd` > 0
- `stock_quantity` ≥ 0
- `isbn` válido (10 o 13 dígitos; se permiten guiones)
- ISBN único
- Fallback si falla la API de cambio
- Manejo de errores: 400, 404, 503 cuando aplique

## Modelo de datos (Book)
Campos principales:
- id (int, PK)
- title (string, max 255)
- author (string, max 255)
- isbn (string, único; válido con 10 o 13 dígitos, admite guiones)
- cost_usd (decimal, > 0)
- selling_price_local (decimal, nullable; se calcula en /calculate-price)
- stock_quantity (entero, >= 0)
- category (string)
- supplier_country (string, ISO 3166-1 alpha-2)
- created_at, updated_at (auto)

## Paginación
- Parámetros: ?page=<n>&page_size=<m>
- Por defecto: page_size=10

## Ejemplos con Postman
- Configuración general:
  - Header: Content-Type = application/json (cuando corresponda).
  - Las URLs usan barra final (ej.: /books/, /books/1/).

- Crear libro
  - Method: POST
  - URL: http://localhost:8000/books/
  - Body: raw → JSON
  ```json
  {
    "title": "El Quijote",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 15.99,
    "stock_quantity": 25,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
  }
  ```

- Listar libros
  - Method: GET
  - URL: http://localhost:8000/books/

- Obtener por ID
  - Method: GET
  - URL: http://localhost:8000/books/1/

- Actualizar (PUT)
  - Method: PUT
  - URL: http://localhost:8000/books/1/
  - Body: raw → JSON
  ```json
  {
    "title": "El Quijote (Edición 2)",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 16.50,
    "stock_quantity": 30,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
  }
  ```

- Eliminar
  - Method: DELETE
  - URL: http://localhost:8000/books/1/

- Buscar por categoría
  - Method: GET
  - URL: http://localhost:8000/books/search/?category=Literatura%20Clásica
  - Params: category = Literatura Clásica

- Stock bajo
  - Method: GET
  - URL: http://localhost:8000/books/low-stock/?threshold=10
  - Params: threshold = 10

- Calcular precio local
  - Method: POST
  - URL: http://localhost:8000/books/1/calculate-price/
  - Body: vacío

## Manejo de errores
- 400 Bad Request:
  - Validaciones: cost_usd <= 0, stock_quantity < 0, isbn inválido, ISBN duplicado.
- 404 Not Found:
  - Recurso inexistente (ej.: /books/9999/).
- 503 Service Unavailable:
  - Falla al obtener tasa de cambio y se determina no disponible (se usa fallback si está configurado).
- 500 Internal Server Error:
  - Error inesperado del servidor (bug o excepción no controlada).

## Notas sobre barra final
- DRF expone rutas con barra final por defecto (ej.: /books/, /books/1/).
- Si configuras APPEND_SLASH=False en settings, también funcionarán sin barra final (ej.: /books, /books/1).
