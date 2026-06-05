from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()

# 当您的 API 应用调用外部 API时，这个过程被称为“回调”。
# 常规 FastAPI 应用
class Invoice(BaseModel):
    id: str
    title: str | None = None
    customer: str
    total: float

class InvoiceEvent(BaseModel):
    description: str
    paid: bool

class InvoiceEventReceived(BaseModel):
    ok: bool

invoices_callback_router = APIRouter()

@invoices_callback_router.post(
    "{$callback_url}/invoices/{$request.body.id}", response_model=InvoiceEventReceived
)

def invoice_notification(body: InvoiceEvent):
    pass

# https://yourapi.com/invoices/?callback_url=https://www.external.org/events
@app.post("/invoices/", callbacks=invoices_callback_router.routes)
def create_invoice(invoice: Invoice, callback_url: HttpUrl | None = None):
    """
    创建发票。

    此操作将会：
    * 把发票发送至客户。
    * 归集现金。
    * 通过回调（向外部 API 发送 POST 请求）通知 API 用户。
    """
    # 在此处实现实际逻辑，例如：
    # httpx.post(callback_url, json={"description": "Invoice paid", "paid": True})
    return {"msg": "Invoice received"}
