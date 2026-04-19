import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, inspect, text, func
from pydantic import BaseModel
from jose import JWTError, jwt
import pandas as pd

# 🆕 IMPORTED FOR DESKTOP APP COMPILATION
import threading
import uvicorn
import webview

# Project Imports
from app.core.database import engine, Base, get_db, SessionLocal
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.core import auth
from app.core.default_inventory import build_essential_products, build_product_image_url

# ==========================================
# 🛠️ APP INITIALIZATION
# ==========================================
app = FastAPI(title="ABUAB Auto Supply ERP", version="5.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================================
# 🛑 ENTERPRISE DATABASE MODELS
# ==========================================

class EnterpriseUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    override_pin = Column(String, nullable=True) 

# 🆕 SHIFT MANAGEMENT (Z-READING)
class ShiftLog(Base):
    __tablename__ = "shift_logs"
    id = Column(Integer, primary_key=True, index=True)
    cashier_username = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    starting_cash = Column(Float, default=0.0)
    expected_cash = Column(Float, nullable=True)
    actual_cash = Column(Float, nullable=True)
    status = Column(String, default="OPEN") # OPEN or CLOSED

class MasterSale(Base):
    __tablename__ = "master_sales"
    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shift_logs.id")) # 🆕 Linked to Shift
    cashier_name = Column(String)
    total_amount = Column(Float)
    discount_applied = Column(Float, default=0.0)
    amount_tendered = Column(Float, default=0.0) # 🆕 Cash handed by customer
    change_due = Column(Float, default=0.0)      # 🆕 Change given back
    status = Column(String, default="COMPLETED") 
    void_reason = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    master_sale_id = Column(Integer, ForeignKey("master_sales.id"))
    product_id = Column(Integer)
    qty = Column(Integer)
    price_at_sale = Column(Float)

class ReturnLog(Base):
    __tablename__ = "return_logs"
    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shift_logs.id")) # 🆕 Linked to Shift
    sale_id = Column(Integer, ForeignKey("master_sales.id"))
    product_id = Column(Integer)
    qty = Column(Integer)
    reason = Column(String) 
    refund_amount = Column(Float)
    processed_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    action = Column(String)
    severity = Column(String, default="INFO") 
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- SCHEMAS ---
class CartItem(BaseModel): 
    product_id: int 
    qty: int

class CheckoutCart(BaseModel): 
    items: List[CartItem]
    discount_percent: float = 0.0
    amount_tendered: float = 0.0 # 🆕 Added to request
    supervisor_pin: Optional[str] = None

class VoidRequest(BaseModel): 
    sale_id: int
    reason: str
    supervisor_pin: str

class UserResponse(BaseModel): 
    id: int
    username: str
    role: str
    class Config: 
        from_attributes = True

class ReturnRequest(BaseModel): 
    sale_id: int
    product_id: int
    qty: int
    reason: str
    supervisor_pin: Optional[str] = None

class ShiftStart(BaseModel): 
    starting_cash: float

class ShiftEnd(BaseModel): 
    actual_cash: float

Base.metadata.create_all(bind=engine)


def ensure_product_image_url_column() -> None:
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    product_columns = {column["name"] for column in inspector.get_columns("products")}
    if "image_url" not in product_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR"))


def is_valid_external_image_url(url: Optional[str]) -> bool:
    if not url:
        return False

    candidate = url.strip()
    if not candidate:
        return False

    parsed = urlparse(candidate)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def resolve_product_image_url(
    name: str,
    category: str,
    item_number: int,
    external_url: Optional[str] = None,
) -> str:
    if is_valid_external_image_url(external_url):
        return external_url.strip()
    return build_product_image_url(name, category, item_number)


def seed_essential_inventory() -> None:
    db = SessionLocal()
    try:
        default_products = build_essential_products()
        has_changes = False

        for item in default_products:
            existing = db.query(Product).filter(Product.sku == item["sku"]).first()
            if existing:
                # Keep essential catalog entries aligned with the curated 100-item list.
                if existing.name != item["name"]:
                    existing.name = item["name"]
                    has_changes = True
                if existing.category != item["category"]:
                    existing.category = item["category"]
                    has_changes = True
                if existing.image_url != item["image_url"]:
                    existing.image_url = item["image_url"]
                    has_changes = True

                # Fill defaults only when missing/invalid to avoid overriding operator edits.
                if existing.stock_quantity is None or existing.stock_quantity < 0:
                    existing.stock_quantity = item["stock_quantity"]
                    has_changes = True
                if existing.price is None or existing.price <= 0:
                    existing.price = item["price"]
                    has_changes = True
                continue

            db.add(Product(**item))
            has_changes = True

        if has_changes:
            db.commit()
    finally:
        db.close()


def ensure_all_products_have_images() -> None:
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        has_changes = False

        if not products:
            return

        for item in products:
            resolved = resolve_product_image_url(
                item.name,
                item.category or "General",
                item.id or 1,
                item.image_url,
            )
            if item.image_url != resolved:
                item.image_url = resolved
                has_changes = True

        if has_changes:
            db.commit()
    finally:
        db.close()


ensure_product_image_url_column()
seed_essential_inventory()
ensure_all_products_have_images()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# ==========================================
# 🔐 SECURITY & LOGGING
# ==========================================

def log_audit(db: Session, username: str, action: str, severity: str = "INFO"):
    db.add(ActivityLog(username=username, action=action, severity=severity))
    db.commit()


def normalize_role(role: str) -> str:
    normalized = (role or "").strip().lower()
    if normalized not in {"staff", "supervisor", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    return normalized


def require_roles(user: dict, allowed_roles: set[str]) -> None:
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

def verify_supervisor_pin(db: Session, pin: str):
    manager = db.query(EnterpriseUser).filter(EnterpriseUser.override_pin == pin).first()
    if not manager or manager.role not in ["admin", "supervisor"]: 
        raise HTTPException(status_code=403, detail="Invalid Manager PIN")
    return manager

@app.get("/login", response_class=HTMLResponse)
def login_page(): 
    return Path(os.path.join(BASE_DIR, "templates", "login.html")).read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def dashboard(): 
    return Path(os.path.join(BASE_DIR, "templates", "index.html")).read_text(encoding="utf-8")

@app.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    pin: str = Form(None),
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
):
    clean_username = username.strip()
    if len(clean_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(password.strip()) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    normalized_role = normalize_role(role)
    existing_user_count = db.query(func.count(EnterpriseUser.id)).scalar() or 0

    if existing_user_count > 0:
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")
        requesting_user = get_current_user(token, db)
        require_roles(requesting_user, {"admin"})
    elif normalized_role != "admin":
        raise HTTPException(status_code=400, detail="First account must be admin")

    if pin:
        normalized_pin = pin.strip()
        if len(normalized_pin) != 4 or not normalized_pin.isdigit():
            raise HTTPException(status_code=400, detail="PIN must be exactly 4 digits")
    else:
        normalized_pin = None

    if db.query(EnterpriseUser).filter(EnterpriseUser.username == clean_username).first():
        raise HTTPException(status_code=400, detail="Username taken")

    db.add(
        EnterpriseUser(
            username=clean_username,
            hashed_password=auth.hash_password(password),
            role=normalized_role,
            override_pin=normalized_pin,
        )
    )
    db.commit()
    return {"message": "Success"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(EnterpriseUser).filter(EnterpriseUser.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password): 
        raise HTTPException(status_code=401, detail="Invalid credentials")
    log_audit(db, user.username, "System Login")
    return {"access_token": auth.create_access_token(data={"sub": user.username}), "token_type": "bearer"}

@app.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_error = HTTPException(status_code=401, detail="Invalid Session")
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_error
        user = db.query(EnterpriseUser).filter(EnterpriseUser.username == username).first()
        if not user:
            raise credentials_error
        return {"id": user.id, "username": user.username, "role": normalize_role(user.role)}
    except (JWTError, HTTPException):
        raise credentials_error

# ==========================================
# 🕒 SHIFT MANAGEMENT (NEW)
# ==========================================
@app.get("/shift/current")
def get_current_shift(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    shift = db.query(ShiftLog).filter(ShiftLog.cashier_username == user["username"], ShiftLog.status == "OPEN").first()
    return {"shift_id": shift.id, "starting_cash": shift.starting_cash} if shift else None

@app.post("/shift/start")
def start_shift(req: ShiftStart, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if db.query(ShiftLog).filter(ShiftLog.cashier_username == user["username"], ShiftLog.status == "OPEN").first():
        raise HTTPException(status_code=400, detail="Shift already open")
    new_shift = ShiftLog(cashier_username=user["username"], starting_cash=req.starting_cash)
    db.add(new_shift)
    db.commit()
    log_audit(db, user["username"], f"Opened Shift. Drawer Float: ₱{req.starting_cash:.2f}")
    return {"status": "Shift Opened"}

@app.post("/shift/end")
def end_shift(req: ShiftEnd, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    shift = db.query(ShiftLog).filter(ShiftLog.cashier_username == user["username"], ShiftLog.status == "OPEN").first()
    if not shift: 
        raise HTTPException(status_code=400, detail="No open shift found")
    
    # Calculate Expected Cash
    sales = db.query(MasterSale).filter(MasterSale.shift_id == shift.id, MasterSale.status == "COMPLETED").all()
    returns = db.query(ReturnLog).filter(ReturnLog.shift_id == shift.id).all()
    
    total_sales = sum(s.total_amount for s in sales)
    total_refunds = sum(r.refund_amount for r in returns)
    
    # 🛑 MATH FIX: Since RMAs now properly deduct from sale.total_amount, we DO NOT subtract refunds twice here!
    expected = shift.starting_cash + total_sales
    discrepancy = req.actual_cash - expected

    shift.expected_cash = expected
    shift.actual_cash = req.actual_cash
    shift.end_time = datetime.utcnow()
    shift.status = "CLOSED"
    db.commit()
    
    severity = "WARNING" if discrepancy != 0 else "INFO"
    log_audit(db, user["username"], f"Closed Shift (Z-Read). Discrepancy: ₱{discrepancy:.2f}", severity)
    
    return {
        "starting_cash": shift.starting_cash,
        "total_sales": total_sales,
        "total_refunds": total_refunds,
        "expected_cash": expected,
        "actual_cash": req.actual_cash,
        "discrepancy": discrepancy
    }

# ==========================================
# 🛒 SALES & CHECKOUT
# ==========================================
@app.get("/products/", response_model=List[ProductResponse])
def get_products(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    get_current_user(token, db)
    products = db.query(Product).all()
    has_changes = False

    for product in products:
        resolved = resolve_product_image_url(
            product.name,
            product.category or "General",
            product.id or 1,
            product.image_url,
        )
        if product.image_url != resolved:
            product.image_url = resolved
            has_changes = True

    if has_changes:
        db.commit()

    return products

@app.post("/products/", response_model=ProductResponse)
def add_product(item: ProductCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin", "supervisor"})

    product_data = item.model_dump()
    lock_hint = 1000 + (sum(ord(ch) for ch in product_data.get("sku", "")) % 9000)
    product_data["image_url"] = resolve_product_image_url(
        product_data["name"],
        product_data["category"],
        lock_hint,
        product_data.get("image_url"),
    )

    new_item = Product(**product_data)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    log_audit(db, user["username"], f"Ingested asset: {item.name}")
    return new_item

@app.delete("/products/{id}")
def delete_product(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin"})
    item = db.query(Product).filter(Product.id == id).first()
    if item:
        db.delete(item)
        db.commit()
        log_audit(db, user["username"], f"Purged asset: {item.name}", "WARNING")
    return {"message": "Deleted"}

@app.post("/restock/{id}")
def restock_item(id: int, added_qty: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin", "supervisor"})
    if added_qty <= 0:
        raise HTTPException(status_code=400, detail="added_qty must be greater than zero")

    item = db.query(Product).filter(Product.id == id).first()
    if item:
        item.stock_quantity += added_qty
        db.commit()
    return {"message": "Restocked"}

@app.post("/checkout/")
def secure_checkout(cart: CheckoutCart, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    shift = db.query(ShiftLog).filter(ShiftLog.cashier_username == user["username"], ShiftLog.status == "OPEN").first()
    if not shift: 
        raise HTTPException(status_code=400, detail="No Open Shift. Please start shift first.")

    approver = None
    if cart.discount_percent > 10.0:
        if user["role"] == "staff":
            if not cart.supervisor_pin: 
                raise HTTPException(status_code=403, detail="Manager PIN required")
            approver = verify_supervisor_pin(db, cart.supervisor_pin).username

    new_sale = MasterSale(shift_id=shift.id, cashier_name=user["username"], total_amount=0.0, discount_applied=0.0, approved_by=approver)
    db.add(new_sale)
    db.flush() 

    subtotal = 0.0
    for c in cart.items:
        db_item = db.query(Product).filter(Product.id == c.product_id).first()
        if not db_item or db_item.stock_quantity < c.qty:
            db.rollback()
            raise HTTPException(status_code=400, detail="Stock error")
        db_item.stock_quantity -= c.qty
        subtotal += (db_item.price * c.qty)
        db.add(SaleItem(master_sale_id=new_sale.id, product_id=c.product_id, qty=c.qty, price_at_sale=db_item.price))

    disc = subtotal * (cart.discount_percent / 100)
    final_total = subtotal - disc
    
    if cart.amount_tendered > 0 and cart.amount_tendered < final_total:
        db.rollback()
        raise HTTPException(status_code=400, detail="Amount tendered is less than total")

    new_sale.total_amount = final_total
    new_sale.discount_applied = disc
    new_sale.amount_tendered = cart.amount_tendered
    new_sale.change_due = cart.amount_tendered - final_total if cart.amount_tendered > 0 else 0.0

    db.commit()
    log_audit(db, user["username"], f"Executed TRX #{new_sale.id} for ₱{final_total}")
    return {"status": "success", "change_due": new_sale.change_due, "transaction_id": new_sale.id}

@app.post("/void-sale/")
def void_transaction(req: VoidRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    approver = user["username"]
    if user["role"] == "staff":
        if not req.supervisor_pin: 
            raise HTTPException(status_code=403, detail="PIN Required")
        approver = verify_supervisor_pin(db, req.supervisor_pin).username

    sale = db.query(MasterSale).filter(MasterSale.id == req.sale_id).first()
    if not sale or sale.status == "VOIDED": 
        raise HTTPException(status_code=400, detail="Invalid Void")

    # 🛑 CORRECT LOGIC: Mirroring Assets. Voids restore ALL items back to the shelf.
    for s_item in db.query(SaleItem).filter(SaleItem.master_sale_id == sale.id).all():
        prod = db.query(Product).filter(Product.id == s_item.product_id).first()
        if prod: 
            prod.stock_quantity += s_item.qty

    sale.status = "VOIDED"
    sale.void_reason = req.reason
    sale.approved_by = approver
    db.commit()
    log_audit(db, user["username"], f"VOIDED TRX #{req.sale_id}. Authorized by {approver}", "CRITICAL")
    return {"status": "Voided"}

@app.get("/sales/{sale_id}")
def get_sale_details(sale_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    sale = db.query(MasterSale).filter(MasterSale.id == sale_id).first()
    if not sale: 
        raise HTTPException(status_code=404, detail="Transaction not found")
    items = db.query(SaleItem).filter(SaleItem.master_sale_id == sale_id).all()
    item_list = []
    for item in items:
        returned = db.query(ReturnLog).filter(ReturnLog.sale_id == sale_id, ReturnLog.product_id == item.product_id).all()
        returned_qty = sum([r.qty for r in returned])
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        item_list.append({ 
            "product_id": item.product_id, 
            "name": prod.name if prod else "Unknown Asset", 
            "purchased_qty": item.qty, 
            "returned_qty": returned_qty, 
            "available_qty": item.qty - returned_qty, 
            "price": item.price_at_sale 
        })
    return {"sale": sale, "items": item_list}

@app.post("/returns/")
def process_rma(req: ReturnRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    shift = db.query(ShiftLog).filter(ShiftLog.cashier_username == user["username"], ShiftLog.status == "OPEN").first()
    if not shift: 
        raise HTTPException(status_code=400, detail="No Open Shift. Cannot process return cash.")

    approver = user["username"]
    if user["role"] == "staff":
        if not req.supervisor_pin: 
            raise HTTPException(status_code=403, detail="Manager PIN Required")
        approver = verify_supervisor_pin(db, req.supervisor_pin).username

    sale = db.query(MasterSale).filter(MasterSale.id == req.sale_id).first()
    if not sale or sale.status == "VOIDED": 
        raise HTTPException(status_code=400, detail="Invalid Transaction")

    sale_item = db.query(SaleItem).filter(SaleItem.master_sale_id == req.sale_id, SaleItem.product_id == req.product_id).first()
    if not sale_item: 
        raise HTTPException(status_code=400, detail="Item not in transaction")

    discount_factor = 1.0
    if sale.discount_applied > 0: 
        discount_factor = 1.0 - (sale.discount_applied / (sale.total_amount + sale.discount_applied))
    refund_amt = (sale_item.price_at_sale * req.qty) * discount_factor

    # 🛑 CORRECT LOGIC: Mirroring Assets. RMAs return items to shelf unless defective.
    prod = db.query(Product).filter(Product.id == req.product_id).first()
    if prod and req.reason != "Defective": 
        prod.stock_quantity += req.qty

    # 🛑 MATH FIX: We must deduct the refund from the sale's total amount so the frontend Dashboard updates!
    sale.total_amount -= refund_amt

    new_return = ReturnLog(
        shift_id=shift.id, 
        sale_id=req.sale_id, 
        product_id=req.product_id, 
        qty=req.qty, 
        reason=req.reason, 
        refund_amount=refund_amt, 
        processed_by=approver
    )
    db.add(new_return)
    db.commit()
    log_audit(db, user["username"], f"RMA Processed: TRX #{req.sale_id}, Refund: ₱{refund_amt:.2f}. Reason: {req.reason}", "WARNING")
    return {"status": "success", "refund": refund_amt}

@app.get("/sales-history/")
def get_sales_history(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin", "supervisor"})
    return db.query(MasterSale).all()

@app.get("/analytics/")
def get_analytics(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin", "supervisor"})
    logs = db.query(ActivityLog).order_by(ActivityLog.id.desc()).limit(15).all()
    sales = db.query(MasterSale).order_by(MasterSale.id.desc()).limit(10).all()
    shifts = db.query(ShiftLog).order_by(ShiftLog.id.desc()).limit(5).all()
    return {"logs": logs, "sales": sales, "shifts": shifts}

@app.get("/users/", response_model=List[UserResponse])
def get_all_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): 
    user = get_current_user(token, db)
    require_roles(user, {"admin"})
    return db.query(EnterpriseUser).all()

@app.delete("/users/{id}")
def delete_user_account(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin"})

    if user["id"] == id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    db_user = db.query(EnterpriseUser).filter(EnterpriseUser.id == id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return {"status": "deleted"}

@app.get("/export-inventory")
def export_inventory(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    require_roles(user, {"admin", "supervisor"})
    products = db.query(Product).all()
    df = pd.DataFrame([{"ID": p.id, "SKU": p.sku, "Name": p.name, "Stock": p.stock_quantity, "Price": p.price} for p in products])
    file_path = os.path.join(BASE_DIR, "ABUAB_Inventory_Report.xlsx")
    df.to_excel(file_path, index=False)
    return FileResponse(path=file_path, filename="ABUAB_Inventory_Report.xlsx")


# ==========================================
# 🖥️ DESKTOP APP ENGINE (PYWEBVIEW)
# ==========================================

def run_fastapi_server():
    """Starts the FastAPI backend in a background thread so the UI can run"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    # 1. Start the server secretly in the background
    server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    server_thread.start()

    # 2. Create the native, locked-down Desktop Window pointing to the local server
    webview.create_window(
        title="ABUAB ENTERPRISE COMMAND",
        url="http://127.0.0.1:8000",
        width=1366,
        height=768,
        min_size=(1024, 768),
        confirm_close=True,          # Asks "Are you sure you want to exit?" to prevent accidental closes
        background_color='#090e17'   # Matches your dark theme perfectly
    )
    
    # 3. Launch the window
    webview.start()