
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from backend.app.api.resume_routes import router as resume_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NOVA",
    description="AI-Powered Talent Intelligence and Resume Classification Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to NOVA",
        "project": "AI-Powered Talent Intelligence Platform",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Fix Swagger UI multiple-file upload display
def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    # Use OpenAPI 3.0.3 for Swagger file upload compatibility
    schema["openapi"] = "3.0.3"

    components = schema.get("components", {}).get("schemas", {})

    for component in components.values():

        properties = component.get("properties", {})

        for prop in properties.values():

            # Multiple file upload
            if prop.get("type") == "array":
                items = prop.get("items", {})

                if items.get("contentMediaType"):
                    items.pop("contentMediaType", None)
                    items["format"] = "binary"

            # Single file upload
            if prop.get("type") == "string":
                if prop.get("contentMediaType"):
                    prop.pop("contentMediaType", None)
                    prop["format"] = "binary"

    app.openapi_schema = schema

    return app.openapi_schema


app.openapi = custom_openapi
