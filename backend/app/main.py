import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.routes import (
    orders, fulfillment, inventory, nodes, shipments, delivery, exceptions, analytics
)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Order Fulfillment and Delivery Promise Optimization System",
    description=(
        "Production-grade Decision Engine for e-commerce and retail supply chains. "
        "Intelligently evaluates available inventory, warehouse capacity, carrier transit, "
        "and cutoffs using a configurable weighted multi-factor scoring algorithm."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with API prefix
api_prefix = settings.API_PREFIX

app.include_router(orders.router, prefix=api_prefix)
app.include_router(fulfillment.router, prefix=api_prefix)
app.include_router(inventory.router, prefix=api_prefix)
app.include_router(nodes.router, prefix=api_prefix)
app.include_router(shipments.router, prefix=api_prefix)
app.include_router(delivery.router, prefix=api_prefix)
app.include_router(exceptions.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": settings.DATABASE_URL.split("://")[0]
    }

# Mount static frontend build if present
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Allow API and Docs to pass through
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return None
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "Frontend build index.html not found"}
else:
    @app.get("/")
    def root():
        return {
            "system": settings.APP_NAME,
            "status": "OPERATIONAL",
            "version": "2.0.0",
            "api_docs": "/docs",
            "api_prefix": api_prefix
        }

