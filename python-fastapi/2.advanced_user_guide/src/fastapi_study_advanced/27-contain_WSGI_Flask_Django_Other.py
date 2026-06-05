from a2wsgi import WSGIMiddleware, ASGIMiddleware
from fastapi import FastAPI
from flask import Flask, request
from markupsafe import escape

app = FastAPI()

# WSGI（Web Server Gateway Interface）是Python定义的一种标准接口，
# 用于连接Web服务器和Web应用程序或框架。它解决了不同Web框架与服务器之间的兼容性问题，
# 使开发者可以自由选择框架和服务器，而无需担心兼容性问题

# 使用 WSGIMiddleware 来包装你的 WSGI 应用，如：Flask，Django，等等
flask_app = Flask(__name__)
@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"

# # http://127.0.0.1:8080/v2
@app.get("/v2")
def read_main():
    return {"message": "Hello World"}

# http://127.0.0.1:8080/v1
app.mount("/v1", WSGIMiddleware(flask_app))