from fastapi import FastAPI
from app.database import create_tables
from app.routes.auth         import router as auth_router
from app.routes.users        import router as users_router
from app.routes.transactions import router as transactions_router
from app.routes.dashboard    import router as dashboard_router

tags_metadata = [
    {"name": "Auth",         "description": "Authentication endpoints"},
    {"name": "Users",        "description": "User management (Admin only)"},
    {"name": "Transactions", "description": "Financial transaction operations"},
    {"name": "Dashboard",    "description": "Dashboard analytics and summaries"},
]

app = FastAPI(
    title="Finance Backend API",
    description="Finance Dashboard Backend",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
def on_startup():
    create_tables()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)
