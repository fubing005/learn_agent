from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

# 应用程序可以携带一些数据调用他们的应用程序（给它们发送请求）
# 这通常被称为网络钩子（Webhook）
class Subscription(BaseModel):
    username: str
    monthly_fee: float
    start_date: datetime

# ✅ 仅生成文档，让用户知道你会发什么数据
@app.webhooks.post("new-subscription")
def new_subscription(body: Subscription):
    """
    当有新用户订阅时，我们会向你在控制台注册的 URL
    发送一个包含此数据的 POST 请求。
    """

# ✅ 这里才是真正触发 webhook 的地方
@app.post("/subscribe/")
def subscribe(subscription: Subscription):
    # 1. 处理订阅逻辑（存数据库等）
    
    # 2. 从数据库查出用户注册的 webhook URL
    user_webhook_url = "https://他的网站.com/webhook"  # 实际从数据库取
    
    # 3. 主动发送通知给用户
    httpx.post(user_webhook_url, json={
        "username": subscription.username,
        "monthly_fee": subscription.monthly_fee
    })
    
    return {"msg": "订阅成功"}

@app.get("/users/")
def read_users():
    return ["Rick", "Morty"]
