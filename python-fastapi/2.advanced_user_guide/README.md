# fastapi-study-advanced

# 相关概念

## OpenAPI 规范
##### 什么是 OpenAPI 规范？

你可以把 OpenAPI 规范理解为一份**"API 的说明书标准"**。

就像建筑图纸有统一的画法规范一样，OpenAPI 规定了**如何用一种统一的格式来描述你的 API**。

------

##### 打个比方 🌰

想象你开了一家餐厅：

- **菜单** = 你的 API 文档
- **菜单的格式规范**（比如要写菜名、价格、食材）= OpenAPI 规范

有了统一的格式，不管是哪家餐厅的菜单，大家都能看懂。

------

##### OpenAPI 规范包含什么？

| 内容     | 例子                           |
| :------- | :----------------------------- |
| API 路径 | `/users/`、`/items/{id}`       |
| 请求方式 | `GET`、`POST`、`PUT`、`DELETE` |
| 参数说明 | 需要传什么参数、什么类型       |
| 数据格式 | 请求体和响应体的结构           |
| 安全认证 | 如何鉴权                       |

------

##### FastAPI 和 OpenAPI 的关系

FastAPI 会**自动**根据你写的代码生成符合 OpenAPI 规范的说明书（一个 JSON 文件），你可以直接访问查看：

```
http://127.0.0.1:8000/openapi.json
```

有了这份说明书，可以自动生成：

- 📄 **交互式文档**（Swagger UI / ReDoc）
- 💻 **客户端代码**（前端、移动端、IoT 等）

[[OpenAPI 介绍](https://fastapi.tiangolo.com/tutorial/first-steps/#openapi)]

------

**一句话总结：OpenAPI 规范就是一套描述 API 的通用标准格式，FastAPI 帮你自动生成它。**


---

## **自定义唯一 ID 生成函数**

##### 什么是"自定义唯一 ID 生成函数"？

------

##### 先理解"操作 ID"是什么

FastAPI 里每个 API 接口都会自动分配一个**唯一的名字**，叫做 **Operation ID**。

比如你有这样一个接口：

```
@app.get("/items/") async def get_items():    ...
```

FastAPI 默认会给它起一个名字，类似：

```
get_items_items__get
```

这个名字又长又丑，包含了路径和 HTTP 方法信息。😕

------

##### 有什么问题？

当你用 FastAPI 自动生成前端客户端代码时，这个 ID 会直接变成**方法名**，结果就是：

```
// 又长又难看 😢 await client.getItemsItemsGet()
```

------

##### 自定义函数能解决什么？

你可以自己写一个函数，**告诉 FastAPI 用什么规则来起名字**，比如用"标签 + 函数名"：

```
from fastapi.routing import APIRoute def custom_generate_unique_id(route: APIRoute):    return f"{route.tags[0]}-{route.name}"    #        ↑ 标签名              ↑ 函数名 app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
```

这样生成的 ID 就变成了：

```
items-get_items   ✅ 简洁多了！
```

前端生成的方法名也随之变得好看：

```
// 简洁易懂 😊 await client.itemsGetItems()
```

------

##### 一句话总结

**自定义唯一 ID 生成函数** = 告诉 FastAPI 用你自己的规则给每个接口起名字，让自动生成的客户端代码方法名更简洁好看。

[[自定义唯一 ID 生成函数](https://fastapi.tiangolo.com/advanced/generate-clients/#custom-operation-ids-and-better-method-names)]

---

## **严格的Content-Type 检查-攻击示例**

##### 通俗解释"严格的 Content-Type 检查 - 攻击示例"

------

##### 先理解几个基本概念

**CORS 预检（Preflight）** 是浏览器的一种保护机制：

"在发送跨域请求之前，先问一下对方服务器：'我可以发吗？'"

但是！浏览器有一个**例外规则**：

如果请求**没有 Content-Type 头**，浏览器认为这是"普通请求"，**直接发送，不问了**。

攻击者正是利用了这个漏洞。

------

##### 用生活场景打比方 🌰

想象一个**小区门禁系统**：

- 小区 = 你的本地电脑
- 门卫 = 浏览器的 CORS 机制
- 快递员 = 恶意网站发来的请求

正常情况下：

```
陌生快递员来了 
门卫：你是哪里来的？有通行证吗？（CORS 预检） 
快递员：我从外面来的，没有通行证 
门卫：不让进！❌
```

但是有个漏洞：

```
陌生快递员穿了"普通访客"的衣服（没有 Content-Type 头） 
门卫：哦，普通访客，直接进吧！✅（不做预检） 
快递员：成功进入小区，为所欲为！😈
```

------

##### 回到攻击示例的具体流程

```
第一步：你在本地运行了一个没有认证的 AI 服务
	http://localhost:8000/v1/agents/multivac 
第二步：你打开了一个恶意网站        
	https://evilhackers.example.com 
第三步：恶意网站偷偷执行这段代码👇
```

```
// 恶意网站偷偷运行的代码 
fetch("http://localhost:8000/v1/agents/multivac", {    
	method: "POST",    
	body: new Blob(['{"action": "send_angry_message"}'])    
	// ⚠️ 注意：故意不设置 Content-Type！ 
})
```

```
第四步：浏览器判断        
	❓ 有 Content-Type 吗？→ 没有        
	❓ 有认证信息吗？    → 没有        
	✅ 那就直接发吧，不做预检！ 
第五步：请求成功到达你的本地 AI 服务        
	AI 服务：收到指令，执行！        
	结果：替你给前老板发了一封愤怒的邮件 😅
```

##### 为什么 FastAPI 的严格检查能防御这个攻击？

```
恶意请求到达 FastAPI 
FastAPI：你有 Content-Type 头吗？ 
恶意请求：没有... 
FastAPI：没有就不解析你的请求体！❌ 攻击失败！
```

[[严格的 Content-Type 检查](https://fastapi.tiangolo.com/advanced/strict-content-type/#strict-content-type-checking)]

------

##### 一句话总结

恶意网站通过**故意不设置 Content-Type 头**来欺骗浏览器跳过安全检查，从而偷偷向你本地运行的服务发送请求。FastAPI 的严格检查就是在服务端**再加一道门**，没有 Content-Type 头的请求一律拒绝解析。