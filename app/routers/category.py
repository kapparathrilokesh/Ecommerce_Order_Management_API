from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryResponse
from app.auth.dependencies import require_role


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# Create Category - Admin only
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = Category(
        name=category_data.name
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# Get Categories - Public
@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):
    return db.query(Category).all()


# Get Category - Public
@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# Update Category - Admin only
@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_category = db.query(Category).filter(
        Category.name == category_data.name,
        Category.id != category_id
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category.name = category_data.name

    db.commit()
    db.refresh(category)

    return category


# Delete Category - Admin only
@router.delete(
    "/{category_id}"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Admin"))
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check whether active products exist
    active_products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).first()

    if active_products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with active products"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }