from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
class ExpenseBase(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=60)
    transaction_type: str = "expense"
    spent_on: date
    description: str | None = None
class ExpenseCreate(ExpenseBase):
    pass
class ExpenseUpdate(ExpenseBase):
    pass
class ExpenseOut(ExpenseBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
class BudgetCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    category: str = "Overall"
    limit_amount: float = Field(gt=0)
class BudgetOut(BudgetCreate):
    id: int
    spent: float = 0
    model_config = ConfigDict(from_attributes=True)
