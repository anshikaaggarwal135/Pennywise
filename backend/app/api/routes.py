from datetime import date
from calendar import monthrange
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, Expense, Budget
from app.schemas.schemas import UserCreate, UserLogin, UserOut, Token, ExpenseCreate, ExpenseUpdate, ExpenseOut, BudgetCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/api")
CATEGORIES = ["Salary", "Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Travel", "Groceries", "Other"]

@router.post("/auth/register", response_model=Token, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=data.name.strip(), email=email, hashed_password=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_access_token(str(user.id)), user=user)

@router.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_access_token(str(user.id)), user=user)

@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.get("/categories")
def categories():
    return CATEGORIES

@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(category: str | None = None, transaction_type: str | None = None, start_date: date | None = None, end_date: date | None = None, search: str | None = None, sort: str = "newest", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Expense).filter(Expense.user_id == user.id)
    if category: q = q.filter(Expense.category == category)
    if transaction_type: q = q.filter(Expense.transaction_type == transaction_type)
    if start_date: q = q.filter(Expense.spent_on >= start_date)
    if end_date: q = q.filter(Expense.spent_on <= end_date)
    if search: q = q.filter(Expense.title.ilike(f"%{search}%"))
    if sort == "oldest": q = q.order_by(Expense.spent_on.asc(), Expense.id.asc())
    elif sort == "amount_high": q = q.order_by(Expense.amount.desc())
    elif sort == "amount_low": q = q.order_by(Expense.amount.asc())
    else: q = q.order_by(Expense.spent_on.desc(), Expense.id.desc())
    return q.all()

@router.post("/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.transaction_type not in ("expense", "income"): raise HTTPException(422, "Transaction type must be expense or income")
    item = Expense(**data.model_dump(), user_id=user.id); db.add(item); db.commit(); db.refresh(item); return item

@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
    if not item: raise HTTPException(404, "Transaction not found")
    if data.transaction_type not in ("expense", "income"): raise HTTPException(422, "Invalid transaction type")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
    if not item: raise HTTPException(404, "Transaction not found")
    db.delete(item); db.commit(); return None

@router.get("/analytics/summary")
def summary(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    month = month or date.today().strftime("%Y-%m")
    try:
        year, mon = map(int, month.split("-")); first = date(year, mon, 1); last = date(year, mon, monthrange(year, mon)[1])
    except (ValueError, TypeError): raise HTTPException(422, "Month must use YYYY-MM format")
    rows = db.query(Expense.transaction_type, func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user.id, Expense.spent_on >= first, Expense.spent_on <= last).group_by(Expense.transaction_type).all()
    totals = {kind: float(value) for kind, value in rows}
    category_rows = db.query(Expense.category, func.sum(Expense.amount)).filter(Expense.user_id == user.id, Expense.transaction_type == "expense", Expense.spent_on >= first, Expense.spent_on <= last).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()
    monthly = []
    for offset in range(5, -1, -1):
        idx = year * 12 + mon - 1 - offset; y, m = divmod(idx, 12); m += 1
        start, end = date(y, m, 1), date(y, m, monthrange(y, m)[1])
        total = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user.id, Expense.transaction_type == "expense", Expense.spent_on >= start, Expense.spent_on <= end).scalar()
        monthly.append({"month": start.strftime("%b %Y"), "expenses": float(total or 0)})
    return {"month": month, "income": totals.get("income", 0), "expenses": totals.get("expense", 0), "balance": totals.get("income", 0)-totals.get("expense", 0), "category_breakdown": [{"category": c, "amount": float(a)} for c,a in category_rows], "monthly_trend": monthly}

@router.get("/budgets")
def list_budgets(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    month = month or date.today().strftime("%Y-%m")
    budgets = db.query(Budget).filter(Budget.user_id == user.id, Budget.month == month).all()
    result = []
    for b in budgets:
        q = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user.id, Expense.transaction_type == "expense", func.strftime("%Y-%m", Expense.spent_on) == month if db.bind.dialect.name == "sqlite" else func.to_char(Expense.spent_on, "YYYY-MM") == month)
        if b.category != "Overall": q = q.filter(Expense.category == b.category)
        spent = float(q.scalar() or 0)
        result.append({"id": b.id, "month": b.month, "category": b.category, "limit_amount": b.limit_amount, "spent": spent})
    return result

@router.post("/budgets", status_code=201)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(Budget).filter(Budget.user_id == user.id, Budget.month == data.month, Budget.category == data.category).first()
    if existing:
        existing.limit_amount = data.limit_amount; db.commit(); db.refresh(existing); return {"id": existing.id, **data.model_dump(), "spent": 0}
    item = Budget(**data.model_dump(), user_id=user.id); db.add(item); db.commit(); db.refresh(item); return {"id": item.id, **data.model_dump(), "spent": 0}

@router.delete("/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not item: raise HTTPException(404, "Budget not found")
    db.delete(item); db.commit(); return None
