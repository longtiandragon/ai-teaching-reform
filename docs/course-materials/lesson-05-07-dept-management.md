# 第05讲：Tlias 部门管理与 RESTful 接口

> 课程来源：07. 后端Web实战(部门管理)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

围绕部门查询、新增、修改、删除实现前后端分离接口，建立统一响应、日志和接口文档意识。

**本讲主线：** 部门管理是第一个完整 CRUD 实战，重点是按接口契约开发，而不是后端单方面“能跑就行”。

## 二、学习目标

- 能按 RESTful 风格设计部门资源接口
- 能实现 Result 统一响应结构
- 能完成部门 CRUD 的 Controller-Service-Mapper 调用链
- 能使用日志定位请求参数与执行结果

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 前后端分离开发流程

前端（Vue/浏览器）通过 HTTP 请求调用后端接口，后端返回 JSON 数据，前端负责渲染展示。前后端通过 **接口文档** 约定数据格式，各自独立开发。

**农博项目的开发顺序**：接口设计 → 写 Mapper XML → 写 Service → 写 Controller → Postman 测试 → 前端联调。

### 2. RESTful 风格 — 从 `NbFarmProduceController` 看接口设计

农博项目中农产品管理模块是标准的 RESTful CRUD：

```java
// 来源: 农博项目/.../controller/NbFarmProduceController.java
@RestController
@RequestMapping("/api/yjnb/produce")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbFarmProduceController {

    @Autowired
    private INbFarmProduceService produceService;

    // 查询列表+分页 — GET /api/yjnb/produce/list?pageNum=1&pageSize=10
    @GetMapping("/list")
    public Result<NbFarmProduce> list(PageQuery pageQuery,
                                      @RequestParam(required = false) String title,
                                      @RequestParam(required = false) String catgory) {
        Map<String, Object> params = buildParams(pageQuery, title, catgory, null, null, null);
        return produceService.selectList(params);   // Service 直接返回带分页的 Result
    }

    // 查询单个 — GET /api/yjnb/produce/{id}
    @GetMapping("/{id}")
    public Result<NbFarmProduce> getById(@PathVariable String id) {
        return Result.success(produceService.selectById(id));
    }

    // 新增 — POST /api/yjnb/produce  (请求体 JSON)
    @PostMapping
    public Result<Void> add(@RequestBody NbFarmProduce produce) {
        produceService.insert(produce);
        return Result.success("Added successfully");
    }

    // 修改 — PUT /api/yjnb/produce
    @PutMapping
    public Result<Void> update(@RequestBody NbFarmProduce produce) {
        produceService.update(produce);
        return Result.success("Updated successfully");
    }

    // 删除 — DELETE /api/yjnb/produce/{id}
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        produceService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    // 批量删除 — DELETE /api/yjnb/produce/batch  (请求体: ["id1","id2"])
    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        produceService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    // 业务操作：推荐 — POST /api/yjnb/produce/recommendFarmProduce
    @PostMapping("/recommendFarmProduce")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);
    }
}
```

**RESTful 风格对照表**：

| HTTP 方法 | 路径示例 | 含义 | 注解 |
|-----------|---------|------|------|
| GET | `/produce/list` | 条件分页查询 | `@GetMapping("/list")` |
| GET | `/produce/{id}` | 查询单个 | `@GetMapping("/{id}")` |
| POST | `/produce` | 新增 | `@PostMapping` |
| PUT | `/produce` | 修改 | `@PutMapping` |
| DELETE | `/produce/{id}` | 删除单条 | `@DeleteMapping("/{id}")` |
| DELETE | `/produce/batch` | 批量删除 | `@DeleteMapping("/batch")` |

**参数接收方式（农博风格）**：

| 注解 | 数据来源 | 农博示例 |
|------|---------|---------|
| `@PathVariable` | URL 路径变量 | `@PathVariable String id` |
| `@RequestBody` | 请求体 JSON | `@RequestBody NbFarmProduce produce` |
| `@RequestParam(required = false)` | URL 查询参数 | `@RequestParam(required = false) String title` |
| 自定义对象（无注解） | 参数自动绑定 | `PageQuery pageQuery`（前端传 `pageNum`, `pageSize`） |

### 3. 统一响应 Result — 农博项目的实际设计

```java
// 来源: 农博项目/.../common/Result.java
@Data
public class Result<T> implements Serializable {
    private Integer code;   // 200=成功, 500=失败
    private String msg;     // 提示信息
    private T data;         // 业务数据（单个对象）
    private Long total;     // 分页总记录数
    private T rows;         // 分页数据列表

    // 成功 — 无数据
    public static <T> Result<T> success() { return new Result<>(200, "操作成功"); }

    // 成功 — 带消息
    public static <T> Result<T> success(String msg) { return new Result<>(200, msg); }

    // 成功 — 带数据
    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>(200, "操作成功");
        result.setData(data);
        return result;
    }

    // 分页成功
    public static <T> Result<T> success(T rows, Long total) {
        Result<T> result = new Result<>(200, "查询成功");
        result.setRows(rows);
        result.setTotal(total);
        return result;
    }

    // 失败
    public static <T> Result<T> error(String msg) { return new Result<>(500, msg); }
}
```

**关键区别**（农博 vs Tlias 教学项目）：

| | 农博 `Result<T>` | Tlias 教学项目 |
|---|---|---|
| 成功码 | `200` | `1` |
| 失败码 | `500`（可自定义） | `0` |
| 分页 | `rows` + `total` 字段，`buildPageData()` 转换为 `data` | `data` 直接包含 |
| 泛型 | `Result<T>` | 无泛型 |

### 4. 完整 CRUD 调用链

**查询列表的完整数据流**（跨越 4 层）：

```
GET /api/yjnb/produce/list?pageNum=1&pageSize=10&title=大米
  → NbFarmProduceController.list(PageQuery, title, catgory)
    → 构建 params Map: {offset:0, pageSize:10, title:"大米", catgory:null, ...}
    → INbFarmProduceService.selectList(params)
      → NbFarmProduceServiceImpl.selectList():
          list = mapper.selectList(params)   ← 执行 XML 中的 SELECT
          total = mapper.selectCount(params) ← 执行 COUNT
          result.setRows(list);              ← 设置分页数据
          result.setTotal(total);
          result.buildPageData();           ← 转为 data = {records, total}
          return result;                    ← 返回封装好的 Result
        ← Result{code:200, msg:"查询成功", data:{records:[...], total:25}}
  ← JSON 响应浏览器
```

**新增的完整调用链**：

```
POST /api/yjnb/produce  {title:"大米", catgory:"谷物", ...}
  → NbFarmProduceController.add(produce)
    → NbFarmProduceServiceImpl.insert(produce):
        if (id == null) produce.setId(UUID.randomUUID().toString().replace("-", ""))
                                                  ← UUID 生成主键
        mapper.insert(produce)                    ← 执行 XML INSERT
        return 1                                  ← 返回影响行数
    → Result.success("Added successfully")
  ← Result{code:200, msg:"Added successfully"}
```

**农博项目特色模式**：
- **分页参数**：用 `PageQuery` 对象（含 `pageNum`, `pageSize`, `getOffset()`），不用 PageHelper
- **查询条件**：Controller 中拼 `Map<String, Object> params` 传给 Mapper，XML 中用 `<if test>` 动态拼接
- **主键策略**：`String` 类型 + `UUID.randomUUID().toString().replace("-", "")`
- **Service 返回 `Result`**：Controller 直接返回 Service 的结果，不在 Controller 中二次包装

## 五、课堂演示

- 搭建 tlias-web-management 工程
- 实现 GET /depts 查询部门
- 实现 POST、PUT、DELETE 并联调前端请求

## 六、课堂练习

- 完成部门管理 CRUD，并为每个接口写出请求方式、路径、参数、响应示例。
- 提交接口说明与关键代码。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 接口路径和 HTTP 方法混乱
- 返回值不统一
- Service 层缺失，Controller 直接访问 Mapper

## 九、AI 助教提示词

- 学生：我正在学习《Tlias 部门管理与 RESTful 接口》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《Tlias 部门管理与 RESTful 接口》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《Tlias 部门管理与 RESTful 接口》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\07. 后端Web实战(部门管理)\PPT\Day07. 后端Web实战(部门管理).pptx（81 页）
- Slide 1: Web 开发 (AI)
- Slide 2: Web 开发 Web 前端基础 Web 后端基础 Web 后端实战 Web 前端实战 Web 项目部署 HTML CSS JavaScript Vue3 Ajax/Axios Maven Web 基础知识 MySQL JDBC Mybatis Tlias 案例 Tlias 案例 Linux Docker
- Slide 3: Web 后端实战 Tlias 智能学习辅助系统
- Slide 4: 需求
- Slide 5: 需求 部门管理 查询、新增、修改、删除 员工管理 查询、新增、修改、删除 文件上传 报表统计 登录认证 日志管理 班级、学员管理（实战内容）
- Slide 6: 需求
- Slide 7: 准备工作 查询部门 删除部门 新增部门 修改部门 日志技术
- Slide 8: 准备工作 开发规范 - 开发模式 开发规范 -Restful 风格 工程搭建 01
- Slide 9: 前后端混合开发 难以维护 分工不明确 不便管理
- Slide 10: 前后端分离开发 当前最为主流的开发模式：前后端分离 接口文档 请求 响应 阅读 - 开发 阅读 - 开发 原型 + 需求 前端开发 后端开发
- Slide 11: 前后端分离开发 接口文档 请求 响应 阅读 - 开发 阅读 - 开发 原型 + 需求 前端开发 后端开发 需求分析 接口设计 (API 接口文档 ) 前后端并行开发 ( 遵守规范 ) 测试 ( 前端、后端 ) 前后端联调测试
- Slide 12: 什么是前后端分离开发 ? 前端项目、后端项目 开发和部署都是分开的。 具体的开发流程 ? 需求分析 -> 接口设计 -> 前后端并行开发 -> 测试 -> 联调
- Slide 14: Restful 接口文档 请求 响应 阅读 - 开发 阅读 - 开发 原型 + 需求 前端开发 后端开发 Restful
- Slide 18: Apifox 思考： 前后端都在并行开发，后端开发完对应的接口之后，如何对接口进行请求测试呢？ 前后端都在并行开发，前端开发过程中，如何获取到数据，测试页面的渲染展示呢？ 接口文档 请求 响应 阅读 - 开发 阅读 - 开发 原型 + 需求 前端开发 后端开发 Restful (POST 、 DELETE 、 PUT 、 GET)

## 十一、配套代码索引

- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\DeptMapper.java`
  - `@Mapper`
  - `public interface DeptMapper {`
  - `//@Select("select id, name, create_time createTime, update_time updateTime from dept order by update_time desc")`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\pojo\Dept.java`
  - `public class Dept {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\pojo\Result.java`
  - `public class Result {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\service\DeptService.java`
  - `public interface DeptService {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\service\impl\DeptServiceImpl.java`
  - `@Service`
  - `public class DeptServiceImpl implements DeptService {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\java\com\itheima\TliasWebManagementApplication.java`
  - `@SpringBootApplication`
  - `public class TliasWebManagementApplication {`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\resources\application.yml`
- `ppt\07. 后端Web实战(部门管理)\代码\tlias-web-management\src\main\resources\logback.xml`
