# 第10讲：登录认证、会话技术、JWT 与拦截器

> 课程来源：12. 后端Web实战(登录认证)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

从用户名密码登录引出登录标记、Cookie/Session、JWT、Filter/Interceptor 和统一登录校验。

**本讲主线：** 登录认证要让学生理解“登录成功后如何在后续请求中证明身份”。

## 二、学习目标

- 能实现用户名密码登录查询
- 理解 Cookie、Session、JWT 的差异
- 能使用拦截器统一校验登录状态
- 能说明 Token 过期、篡改和敏感信息风险

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 登录功能的本质 — 农博项目的 `AuthController`

**登录功能的本质是什么？查询。** 根据用户名和密码查询用户信息，查到 = 登录成功，查不到 = 登录失败。

```java
// 来源: 农博项目/.../controller/AuthController.java
@RestController
@RequestMapping("/api/yjnb/system")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class AuthController {

    @Autowired
    private ISysUserService userService;

    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        // 1. 参数校验
        if (username == null || username.trim().isEmpty()) {
            return Result.error("Username is required");
        }
        if (password == null || password.trim().isEmpty()) {
            return Result.error("Password is required");
        }

        // 2. 查询数据库
        SysUser user = userService.selectByUsername(username);
        if (user == null || !password.equals(user.getPassword())) {
            return Result.error("Username or password is incorrect");
        }

        // 3. 状态校验
        if (user.getStatus() != null && user.getStatus() == 1) {
            return Result.error("User account is disabled");
        }

        // 4. 更新登录信息
        user.setLoginIp("127.0.0.1");
        user.setLoginDate(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        userService.update(user);

        // 5. 生成 Token + 返回用户信息
        Map<String, Object> data = new HashMap<>();
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname() != null ? user.getNickname() : user.getUsername());
        data.put("token", "TOKEN_" + user.getUsername() + "_" + UUID.randomUUID().toString().replace("-", ""));
        data.put("role", "admin".equals(user.getUsername()) ? "超级管理员" : "普通用户");
        data.put("userId", user.getId());
        return Result.success("Login successful", data);
    }
}
```

**登录流程**：参数校验 → 查数据库 → 密码比对 → 状态校验 → 更新登录记录 → 生成 Token → 返回。

### 2. 会话技术 — Cookie/Session/JWT/简单Token 对比

| 技术 | 工作原理 | 农博项目 |
|------|---------|:---:|
| **Cookie** | 服务器在 HTTP 响应头设 `Set-Cookie`，浏览器自动携带 | — |
| **Session** | 服务器创建会话存用户信息，Cookie 只存 SessionId | — |
| **JWT** | 无状态令牌，用户信息编码在 Payload 中，用签名防篡改 | Tlias 教学项目 |
| **简单 Token** | UUID 拼接生成，无签名、无载荷、无过期控制 | ✅ 农博项目 |

**农博使用简单 Token 方式**：

```java
// Token 生成 = 固定前缀 + 用户名 + UUID
String token = "TOKEN_" + user.getUsername() + "_" + UUID.randomUUID().toString().replace("-", "");
```

**简单 Token vs JWT**：

| | JWT（Tlias 教学项目） | 简单 Token（农博项目） |
|---|---|---|
| 结构 | Header.Payload.Signature（三段） | 纯字符串 |
| 是否含用户信息 | Payload 中编码 | 不含（需要另外查数据库） |
| 防篡改 | 签名验证 | 无法验证（需配合服务端存储） |
| 过期控制 | `setExpiration()` 内置 | 需自己实现 |
| 学习门槛 | 需理解签名、Claims | 直观，一看就懂 |
| 适用场景 | 分布式微服务 | 简单前后端分离项目 |

### 3. 跨域处理 — 农博项目的两种方式

前后端分离开发中，前端（localhost:5173）请求后端（localhost:8080）会受到浏览器同源策略限制。

**方式一：`@CrossOrigin` 注解（农博项目每个 Controller 都加）**：

```java
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
```

**方式二：`CorsFilter` 过滤器（农博项目的全局方案）**：

```java
// 来源: 农博项目/.../filter/CorsFilter.java
public class CorsFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
        HttpServletResponse response = (HttpServletResponse) res;
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", "POST, GET, PUT, OPTIONS, DELETE, PATCH");
        response.setHeader("Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept, Authorization, token");

        // OPTIONS 预检请求直接返回 200
        if ("OPTIONS".equalsIgnoreCase(((HttpServletRequest) req).getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        chain.doFilter(req, res);
    }
}
```

**两种方式的选择**：`@CrossOrigin` 简单直接但需要每个 Controller 都写；`CorsFilter` 配置一次全局生效。

### 4. 完整登录数据流

```
POST /api/yjnb/system/login  {username:"admin", password:"123456"}
  → AuthController.login()
    → ISysUserService.selectByUsername("admin")
      → SysUserMapper XML: SELECT * FROM sys_user WHERE username = #{username}
    ← SysUser{id:"xxx", username:"admin", status:0}
    → 密码校验通过 → 更新 loginIp/loginDate
    → 生成 token: "TOKEN_admin_<UUID>"
  ← Result{code:200, msg:"Login successful", data:{token:"TOKEN_admin_...", role:"超级管理员"}}

后续请求 GET /api/yjnb/produce/list (Header: token=TOKEN_admin_...)
  → （农博项目当前未实现拦截器校验，token 仅作为身份标识返回前端）
```

**教师补充说明**：农博项目目前 token 生成后未在后端做拦截器统一校验，这是因为项目处于开发阶段。实际生产项目需要补充 Interceptor 或 Filter 在 `preHandle` 中校验 token 有效性，拦截未登录请求返回 401。

## 五、课堂演示

- POST /login 返回 token
- 前端携带 token 请求部门/员工接口
- 编写 LoginCheckInterceptor 放行登录接口并拦截其他接口
- 演示未登录访问被拒绝

## 六、课堂练习

- 为 Tlias 系统补全登录认证：登录返回 JWT，其他接口通过拦截器校验。
- 提交登录接口、JWT 工具、拦截器配置和失败响应。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 把密码明文写日志
- 忘记放行登录接口
- JWT 密钥硬编码或过期时间缺失

## 九、AI 助教提示词

- 学生：我正在学习《登录认证、会话技术、JWT 与拦截器》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《登录认证、会话技术、JWT 与拦截器》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《登录认证、会话技术、JWT 与拦截器》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\12. 后端Web实战(登录认证)\PPT\12. 后端Web实战(登录认证).pptx（52 页）
- Slide 1: Web 后端开发
- Slide 2: Tlias 智能学习辅助系统
- Slide 4: Web 后端开发 登录认证
- Slide 5: 登录功能 登录校验
- Slide 6: 登录功能 01
- Slide 7: 思路分析 怎么样才算登录成功了呢 ? 用户名和密码都输入正确， 登录成功 否则， 登录失败 登录功能的本质是什么 ? 查询 根据用户名和密码查询员工信息
- Slide 8: 员工登录 - 思路 Controller 接收请求参数 ( 用户名、密码 ) 调用 Service 方法 响应结果 Service 根据用户名和密码查询员工信息 判定，组装数据并返回 Mapper SQL: select * from emp where username = ? and password = ?
- Slide 9: 联调测试 问题： 在未登录情况下，我们也可以直接访问部门管理、员工管理等功能。 需求：只有员工登录成功，才可以访问后台系统中的数据。 浏览器 Web 服务器 请求 响应 登录校验 Login Emp Dept Report
- Slide 10: 登录功能 登录校验
- Slide 11: 登录校验 02
- Slide 12: 登录校验思路 浏览器 Web 服务器 请求 响应 Login Emp Dept Report 登录标记 存 取 统一拦截 登录标记 统一拦截
- Slide 13: 登录校验思路 浏览器 Web 服务器 请求 响应 Login Emp Dept Report 登录标记 统一拦截 存 取 登录标记：用户登录成功之后，在后续的每一次请求中，都可以获取到该标记。 【 会话技术 】 统一拦截：过滤器 Filter 、拦截器 Interceptor
- Slide 14: 登录校验 会话技术 JWT 令牌 过滤器 Filter 拦截器 Interceptor 02
- Slide 15: 会话技术 会话：用户打开浏览器，访问 web 服务器的资源，会话建立，直到有一方断开连接，会话结束。在一次会话中可以包含多次请求和响应。 会话跟踪：一种维护浏览器状态的方法，服务器需要识别多次请求是否来自于同一浏览器，以便在同一次会话的多次请求间共享数据。 会话跟踪方案： 客户端会话跟踪技术： Cookie 服务端会话跟踪技术： Session 令牌技术 W

## 十一、配套代码索引

- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\config\WebConfig.java`
  - `@Configuration`
  - `public class WebConfig implements WebMvcConfigurer {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\ClazzController.java`
  - `@RestController`
  - `public class ClazzController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\EmpController.java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\LoginController.java`
  - `@RestController`
  - `public class LoginController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\ReportController.java`
  - `@RestController`
  - `public class ReportController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\SessionController.java`
  - `@RestController`
  - `public class SessionController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\StudentController.java`
  - `@RestController`
  - `public class StudentController {`
- `ppt\12. 后端Web实战(登录认证)\代码\tlias-web-management\src\main\java\com\itheima\controller\UploadController.java`
  - `@RestController`
  - `public class UploadController {`
