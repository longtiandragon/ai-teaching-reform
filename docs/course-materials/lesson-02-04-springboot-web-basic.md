# 第02讲：SpringBoot Web 入门与分层解耦

> 课程来源：04. 后端Web基础(基础知识)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

从 HTTP 请求处理、Controller 入门、三层架构到 IOC/DI，建立 SpringBoot Web 开发第一条完整调用链。

**本讲主线：** SpringBoot Web 教学的核心不是跑通 /hello，而是让学生看见请求如何进入 Controller，并逐步拆分到 Service/Dao。

## 二、学习目标

- 能创建 SpringBoot Web 工程并暴露 GET 接口
- 能区分静态资源、动态资源和 B/S 架构
- 能描述 Controller、Service、Dao 的职责
- 理解 IOC/DI 如何降低层间耦合

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 三层架构 — 为什么要把代码拆开

**问题驱动**：如果把请求处理、业务判断、数据库操作全部写在一个类里，改一处就要读几百行代码。项目越大，维护越困难。

**农博项目的标准分层**（以"农产品管理"模块为例）：

```
controller/NbFarmProduceController.java   ← 接收 HTTP 请求、参数校验、返回响应
service/INbFarmProduceService.java        ← 接口：定义业务规则
service/impl/NbFarmProduceServiceImpl.java ← 实现：业务逻辑、调用 Mapper
mapper/NbFarmProduceMapper.java           ← 数据访问接口
mapper/NbFarmProduceMapper.xml            ← SQL 映射文件
entity/NbFarmProduce.java                 ← 数据模型（实体类）
common/Result.java                        ← 统一响应结构
```

**各层职责**（农博项目实际代码）：

| 层 | 职责 | 禁止做的事 |
|----|------|-----------|
| Controller | 接收参数 → 构建 `Map<String, Object>` 条件 → 调 Service → 返回 `Result` | 不写 SQL、不写复杂业务逻辑 |
| Service | 调 Mapper 获取数据 → 组装 `Result`（设置 rows/total）→ 返回 `Result` | 不处理 HTTP 请求/响应对象 |
| Mapper | 接口声明方法 + XML 写 SQL | 不写业务判断 |

**农博项目的 Controller 示例**：

```java
// 来源: 农博项目/.../controller/NbFarmProduceController.java
@RestController
@RequestMapping("/api/yjnb/produce")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbFarmProduceController {

    @Autowired
    private INbFarmProduceService produceService;  // 依赖接口，不依赖实现

    @GetMapping("/list")
    public Result<NbFarmProduce> list(PageQuery pageQuery,
                                      @RequestParam(required = false) String title,
                                      @RequestParam(required = false) String catgory) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        params.put("catgory", catgory);
        return produceService.selectList(params);  // Service 直接返回 Result
    }

    @GetMapping("/{id}")
    public Result<NbFarmProduce> getById(@PathVariable String id) {
        return Result.success(produceService.selectById(id));
    }
}
```

**关键注解（农博风格）**：
- `@CrossOrigin(originPatterns = "*", allowCredentials = "true")` — 每个 Controller 都加，允许前端跨域访问
- `@RequestMapping("/api/yjnb/produce")` — 统一的前缀路径
- `@Autowired` — 字段注入（农博项目中使用的风格）

---

### 2. IOC 与 DI — 从 `new` 到 `@Autowired`

**解耦前（反例）**：Controller 直接 new 实现类

```java
// ❌ 紧耦合写法
public class NbFarmProduceController {
    private NbFarmProduceServiceImpl produceService = new NbFarmProduceServiceImpl();
    // 换一个实现类就必须改这行代码
}
```

**解耦后（农博项目实际写法）**：

```java
// ✅ IOC/DI 写法 — 来源: 农博项目/NbFarmProduceController.java
@RestController
public class NbFarmProduceController {

    @Autowired
    private INbFarmProduceService produceService;  // 只依赖接口
    // ...
}
```

同时，Service 实现类必须用 `@Service` 交给 Spring 管理：

```java
// 来源: 农博项目/.../service/impl/NbFarmProduceServiceImpl.java
@Service
public class NbFarmProduceServiceImpl implements INbFarmProduceService {

    @Autowired
    private NbFarmProduceMapper produceMapper;

    @Override
    public int insert(NbFarmProduce produce) {
        if (produce.getId() == null || produce.getId().isEmpty()) {
            produce.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return produceMapper.insert(produce);
    }
}
```

**IOC（控制反转）**：对象的创建权从程序员（`new`）**反转**给了 Spring 容器。你不再自己 `new` 对象，而是告诉 Spring"我需要什么"，Spring 负责创建并给到你。

**DI（依赖注入）**：`@Autowired` 就是 DI 的实现方式——Spring 自动把容器中匹配类型的 Bean 注入到字段上。

**对比表**：

| | 紧耦合（new） | 松耦合（@Autowired） |
|---|---|---|
| 声明方式 | `= new NbFarmProduceServiceImpl()` | `@Autowired INbFarmProduceService` |
| 依赖目标 | 具体实现类 | 接口 `INbFarmProduceService` |
| 换实现 | 改所有用到的地方 | 只改一个类 |
| 方式 | 程序员手动创建 | Spring 容器自动注入 |

**四个分层注解**：

| 注解 | 含义 | 农博项目中的使用 |
|------|------|----------------|
| `@RestController` | 控制器 Bean，返回值自动转 JSON | 所有 Controller |
| `@Service` | 业务层 Bean | `XxxServiceImpl` |
| `@Repository` | 数据访问层 Bean | （农博用 XML，Mapper 不加注解，靠 XML 扫描） |
| `@Component` | 通用 Bean | 工具类、配置类 |

**IOC 容器就像"对象池"**：启动时 Spring 扫描所有带 `@Service/@Component` 的类 → 创建实例 → 放入容器 → 遇到 `@Autowired` 就从容器中取出匹配的 Bean 注入。默认是**单例**（整个容器一个实例）。

**完整调用链**：

```
浏览器 GET /api/yjnb/produce/list?pageNum=1&pageSize=10
  → NbFarmProduceController.list()        [@RestController]
    → 构建 params Map（offset/pageSize/查询条件）
    → INbFarmProduceService.selectList()  [@Service]
      → NbFarmProduceMapper.selectList()  [MyBatis 代理]
        → 执行 XML 中的 SELECT SQL
      ← List<NbFarmProduce>
      → 封装 Result{code:200, rows:[...], total:25}
    ← Result
  ← JSON 响应到浏览器
```

**易错点**：
- `@Autowired` 了但 Service 实现类忘了加 `@Service` → 启动报错：找不到 Bean
- Controller 直接 new → IOC 失效，后续想加事务/AOP 都加不上
- 只背注解名不理解"接口依赖"的价值 → 换实现时要改几十处代码

## 五、课堂演示

- 完成 /hello?name=xxx 接口
- 演示用户列表从 Controller 到 Service 到 Dao 的拆分
- 把 new 对象改为 @Service + 构造器注入

## 六、课堂练习

- 基于资料中的用户列表案例，重构为 Controller-Service-Dao 三层，并说明每层职责。
- 提交接口路径、关键代码和一次请求的调用链说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 把所有逻辑写在 Controller
- 不会解释 @Component、@Service、构造器注入差异
- 返回格式不稳定，前端难以联调

## 九、AI 助教提示词

- 学生：我正在学习《SpringBoot Web 入门与分层解耦》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《SpringBoot Web 入门与分层解耦》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《SpringBoot Web 入门与分层解耦》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\04. 后端Web基础(基础知识)\PPT\Day04-Web基础知识.pptx（70 页）
- Slide 1: Web 后端开发 Web 基础知识
- Slide 3: Web 服务器 静态资源 动态资源 静态资源： 服务器上存储的不会改变的数据，通常不会根据用户的请求而变化。比如： HTML 、 CSS 、 JS 、图片、视频等 ( 负责页面展示 ) 动态资源：服务器端根据用户请求和其他数据动态生成的，内容可能会在每次请求时都发生变化。比如： Servlet 、 JSP 等 ( 负责逻辑处理 ) B/S 架构： Brows
- Slide 4: SpringBoot Web 入门 HTTP 协议 SpringBoot Web 案例 分层解耦
- Slide 5: 01 SpringBoot Web 入门
- Slide 6: 官网： spring.io Spring 发展到今天已经形成了一种开发生态圈， Spring 提供了若干个子项目，每个项目用于完成特定的功能。 Spring 全家桶
- Slide 7: 官网： spring.io Spring 发展到今天已经形成了一种开发生态圈， Spring 提供了若干个子项目，每个项目用于完成特定的功能。 Spring
- Slide 8: Spring 入门难度大 配置繁琐 简化配置 快速开发
- Slide 9: SpringBoot Spring Boot 可以帮助我们非常快速的构建应用程序、简化开发、提高效率。
- Slide 10: SpringBoot Web 入门 01 入门程序 入门程序剖析
- Slide 11: 需求：基于 SpringBoot 开发一个 Web 应用，浏览器发起请求 /hello 之后，给浏览器返回一个字符串 "Hello Xxx" 。 入门程序 http://localhost:8080/hello?name=Heima "Hello Heima ~"
- Slide 12: SpringBootWeb 入门程序 ① . 创建 springboot 工程，并勾选 web 开发相关依赖。 ② . 定义 HelloController 类，添加方法 hello ，并添加注解。 http://localhost:8080/hello?name=Heima "Hello Heima ~" public class HelloControl
- Slide 13: SpringBootWeb 快速入门步骤 : 创建 SpringBoot 工程，勾选 web 开发依赖。 定义请求处理类 HelloController ，定义请求处理方法 运行启动类，测试 public class HelloController { public String hello ( String name){ System . out .pri
- Slide 15: SpringBoot Web 入门 01 入门程序 入门程序剖析
- Slide 18: SpringBoot Web 入门 HTTP 协议 SpringBoot Web 案例 分层解耦

## 十一、配套代码索引

- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web入门\springboot-web-quickstart\pom.xml`
  - `<dependency>`
  - `<dependency>`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web入门\springboot-web-quickstart\src\main\java\com\itheima\HelloController.java`
  - `@RestController //标识当前是一个请求处理类`
  - `public class HelloController {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web入门\springboot-web-quickstart\src\main\java\com\itheima\SpringbootWebQuickstartApplication.java`
  - `@SpringBootApplication`
  - `public class SpringbootWebQuickstartApplication {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web入门\springboot-web-quickstart\src\main\resources\application.properties`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web入门\springboot-web-quickstart\src\test\java\com\itheima\SpringbootWebQuickstartApplicationTests.java`
  - `class SpringbootWebQuickstartApplicationTests {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web案例(三层架构拆分)\springboot-web-demo\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web案例(三层架构拆分)\springboot-web-demo\src\main\java\com\itheima\controller\UserController.java`
  - `@RestController //@Controller + @ResponseBody -----> 如果返回的是一个对象/集合 --> 转json --> 响应`
  - `public class UserController {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web案例(三层架构拆分)\springboot-web-demo\src\main\java\com\itheima\dao\impl\UserDaoImpl.java`
  - `public class UserDaoImpl implements UserDao {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web案例(三层架构拆分)\springboot-web-demo\src\main\java\com\itheima\dao\UserDao(1).java`
  - `public interface UserDao {`
- `ppt\04. 后端Web基础(基础知识)\代码\springboot-web案例(三层架构拆分)\springboot-web-demo\src\main\java\com\itheima\dao\UserDao.java`
  - `public interface UserDao {`
