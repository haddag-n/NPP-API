"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.auth.routes import router as auth_router
from app.medicaments.routes import router as medicaments_router
from app.importer.routes import router as import_router
from app.db.session import engine
from app.db.base import Base
from app.auth.models import User
from app.core.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Creates database tables and initial admin user on startup.
    """
    import os
    
    # Create tables (drop first if RECREATE_TABLES is set)
    async with engine.begin() as conn:
        if os.environ.get("RECREATE_TABLES", "").lower() == "true":
            print("⚠️  RECREATE_TABLES=true: Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ Tables dropped")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created/verified")
    
    # Create initial admin user if it doesn't exist
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print(f"✅ Initial admin user created: {settings.ADMIN_EMAIL}")
        else:
            print(f"ℹ️  Admin user already exists: {settings.ADMIN_EMAIL}")
    
    yield
    
    # Cleanup
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API pour la nomenclature nationale des produits pharmaceutiques à usage humain",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status with last import information."""
    from app.db.session import AsyncSessionLocal
    from app.models.import_log import ImportLog
    from sqlalchemy import select
    
    response = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "derniere_mise_a_jour": None
    }
    
    # Get last successful import
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ImportLog)
                .where(ImportLog.end_time.is_not(None))
                .order_by(ImportLog.end_time.desc())
                .limit(1)
            )
            last_import = result.scalar_one_or_none()
            
            if last_import:
                response["derniere_mise_a_jour"] = last_import.version_nomenclature
    except Exception:
        # If database not ready or error, just return basic health
        pass
    
    return response


# Include routers
app.include_router(auth_router)
app.include_router(medicaments_router)
app.include_router(import_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
