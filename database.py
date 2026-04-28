"""
Database connection using PyMySQL (matches your existing SellerOps stack).
Set DATABASE_URL in .env:  mysql+pymysql://user:pass@host/dbname
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/artisanco")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Dependency ────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Models ────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(255), nullable=False, index=True)
    description   = Column(Text, default="")
    category      = Column(String(100), index=True)
    price         = Column(Float, nullable=False)
    mrp           = Column(Float)
    cost_price    = Column(Float)
    stock         = Column(Integer, default=0)
    sku           = Column(String(100), unique=True, nullable=True)
    image_url     = Column(Text, default="")
    emoji         = Column(String(10), default="📦")
    tags          = Column(String(500), default="")
    badge         = Column(String(50), default="")
    status        = Column(String(20), default="active")   # active | draft
    featured      = Column(Boolean, default=False)
    rating        = Column(Float, default=4.5)
    reviews       = Column(Integer, default=0)
    weight        = Column(Float)
    dimensions    = Column(String(100))
    low_stock_alert = Column(Integer, default=10)
    gst           = Column(String(10), default="0%")
    seo_title     = Column(String(255), default="")
    seo_desc      = Column(Text, default="")
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = "categories"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), unique=True, nullable=False)
    visible    = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id            = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255))
    customer_email= Column(String(255))
    items         = Column(Text)          # JSON string of cart items
    total         = Column(Float)
    status        = Column(String(50), default="processing")
    created_at    = Column(DateTime, server_default=func.now())


class SeoSettings(Base):
    __tablename__ = "seo_settings"

    id          = Column(Integer, primary_key=True, default=1)
    store_title = Column(String(255), default="ArtisanCo. — Handcrafted Products")
    meta_desc   = Column(Text, default="")
    keywords    = Column(Text, default="")
    canonical   = Column(String(255), default="https://yourstore.com")
    ga_id       = Column(String(100), default="")
    pixel_id    = Column(String(100), default="")
    og_image    = Column(Text, default="")


# ── Create tables ─────────────────────────────────────────────────
def init_db():
    Base.metadata.create_all(bind=engine)

    # Seed default categories if empty
    db = SessionLocal()
    if db.query(Category).count() == 0:
        for name in ["Home", "Fashion", "Kitchen", "Electronics"]:
            db.add(Category(name=name))
        db.commit()

    # Seed default SEO settings if empty
    if db.query(SeoSettings).count() == 0:
        db.add(SeoSettings())
        db.commit()

    db.close()
