# 第12讲：SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级

> 课程来源：14. 后端Web进阶(SpringBoot原理&Maven高级)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

收束 SpringBoot 工作原理，讲解配置优先级、Bean 作用域、第三方 Bean、自定义 starter、自动配置、多模块、继承聚合和私服。

**本讲主线：** 进阶课把“会用 SpringBoot”推进到“知道 starter、配置和模块化为什么这样工作”。

## 二、学习目标

- 能说明 SpringBoot 配置优先级
- 理解 Bean 作用域和第三方 Bean 注册
- 能解释自动配置和自定义 starter 的基本结构
- 能进行 Maven 分模块、继承和聚合设计

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. SpringBoot 配置优先级

当同一个配置项出现在多个地方时，SpringBoot 按以下优先级（从高到低）：

| 优先级 | 配置来源 | 示例 |
|:---:|------|------|
| 1（最高） | 命令行参数 | `java -jar app.jar --server.port=9090` |
| 2 | 操作系统环境变量 | `SERVER_PORT=9090` |
| 3 | `application-{profile}.yml` | `application-prod.yml` |
| 4 | `application.yml` | `application.yml`（通用） |
| 5 | `@PropertySource` 导入的配置 | `@PropertySource("classpath:db.properties")` |

**课堂演示设计**：在不同地方设置 `server.port`，让学生观察最终生效的是哪个。这是理解"为什么改了 application.yml 端口没变"的关键。

### 2. Bean 作用域与第三方 Bean

**Spring 管理的 Bean 默认是单例**——整个容器只有一个实例。也可通过 `@Scope` 改变：

| 作用域 | `@Scope` 值 | 含义 |
|--------|------------|------|
| singleton | `"singleton"`（默认） | 容器中仅一个实例 |
| prototype | `"prototype"` | 每次注入/获取都创建新实例 |
| request | `"request"` | 每次 HTTP 请求一个实例（Web 环境） |
| session | `"session"` | 每个 HTTP Session 一个实例 |

**注册第三方 Bean**：当你用的 jar 包里的类没有 `@Component` 注解（因为不是你写的），需要用 `@Configuration` + `@Bean` 手动注册：

```java
@Configuration
public class WebConfig {
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();  // 让第三方类进入 Spring 容器
    }
}
```

### 3. 自动配置原理与自定义 starter

**SpringBoot 自动配置的核心**：`@SpringBootApplication` → `@EnableAutoConfiguration` → `@Import(AutoConfigurationImportSelector.class)` → 读所有 jar 包中 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件 → 加载这些类 → `@ConditionalOnClass/@ConditionalOnBean` 等条件注解决定是否生效。

**自定义 starter 的最小结构**（对应你的 `01. 自定义starter` 项目）：
```
aliyun-oss-spring-boot-starter/
├── pom.xml
├── src/main/resources/META-INF/spring/
│   └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
└── src/main/java/.../
    ├── AliyunOSSOperator.java         ← 业务类
    ├── AliyunOSSProperties.java       ← @ConfigurationProperties(prefix = "aliyun.oss")
    └── AliyunOSSAutoConfiguration.java ← @Configuration + @EnableConfigurationProperties
```

**starter 的三个要素**：
1. **Properties 类**：`@ConfigurationProperties(prefix = "xxx")` 绑定配置文件中的属性
2. **自动配置类**：`@Configuration` + `@Bean` 创建并注册 Bean，加 `@ConditionalOnClass` 条件注解
3. **spring.factories/imports 文件**：告诉 SpringBoot 自动加载这个配置类

**`@ConditionalOnClass`**：只有当 classpath 中存在指定类时才创建 Bean——如果没引入相关依赖就跳过，避免启动报错。

### 4. Maven 分模块、继承与聚合

**为什么要分模块**：Tlias 单体项目越写越大，pojo、工具类、web 代码混在一起，修改一处要整体重新打包。

**分模块后的结构**（对应你的 `03. maven分模块之后代码`）：
```
tlias-parent (父工程, pom)
├── tlias-pojo          ← 实体类（被所有模块依赖）
├── tlias-utils         ← 工具类（JwtUtils、CurrentHolder 等）
└── tlias-web-management ← web 层（依赖 pojo + utils）
```

**父 POM 的作用**：统一管理版本号（`<dependencyManagement>`）和插件配置，子模块继承后不用重复声明。

**依赖方向规则**：web-management 依赖 pojo 和 utils；pojo 不依赖任何人。**绝对不能出现循环依赖**（pojo 反过来依赖 web-management）。

**Maven 聚合和继承**：
- **继承**（`<parent>`）：子模块从父 POM 继承版本和配置
- **聚合**（`<modules>`）：父 POM 中声明所有子模块，执行 `mvn compile` 时一次编译全部

**私服（Nexus）简介**：公司内部搭建的 Maven 仓库。自己写的 jar（像 tlias-pojo）可以 `mvn deploy` 上传到私服，团队其他人就能在 pom.xml 中引用——不需要 copy jar 包和源码。

## 五、课堂演示

- 演示不同方式设置 server.port 的优先级
- 注册第三方 Bean 到 Spring 容器
- 拆分 tlias-pojo、tlias-utils、tlias-web-management
- 分析自定义 aliyun-oss starter 的自动配置类

## 六、课堂练习

- 把单体 Tlias 工程拆成 pojo、utils、web-management 三个 Maven 模块，并说明依赖方向。
- 提交模块结构、父 pom、子模块 pom 和依赖说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 配置文件格式混用导致覆盖困惑
- Bean 作用域误用
- 子模块版本不统一或循环依赖

## 九、AI 助教提示词

- 学生：我正在学习《SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web开发总结.pptx（6 页）
- ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web进阶(Maven高级).pptx（35 页）
- ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web进阶(SpringBoot原理).pptx（36 页）
- Slide 1: Web 后端开发 总结
- Slide 2: Web 后端开发 Service Controller Dao MySQL
- Slide 3: Web 后端开发 Service Controller Dao MySQL 过滤器 拦截器 IOC DI AOP 事务管理 全局异常处理 Mybatis 阿里云 OSS JWT Cookie 、 Session
- Slide 4: Web 后端开发 IOC DI AOP 事务管理 全局异常处理 拦截器 Mybatis SpringBoot 阿里云 OSS JWT Cookie 、 Session 过滤器 JavaWeb 解决方案 S pring framework M ybatis web
- Slide 5: Web 后端开发 IOC DI AOP 事务管理 全局异常处理 拦截器 Mybatis SpringBoot S pringMVC M ybatis JWT 阿里云 OSS Cookie 、 Session 过滤器 JavaWeb 解决方案 响应数据 接收请求 S pring framework
- Slide 6: Web 前端实战
- Slide 1: Web 后端开发 Maven 高级
- Slide 2: 分模块设计与开发 继承与聚合 私服
- Slide 3: 分模块设计与开发 01
- Slide 4: 为什么 ? 分模块设计 商品模块 搜索模块 购物车模块 订单模块 ...... 不便维护 难以复用
- Slide 5: 为什么 ? 分模块设计 商品模块 搜索模块 购物车模块 订单模块 分模块设计 商品模块 搜索模块 购物车模块 订单模块 通用组件 将一个大项目 拆分成若干个子模块，方便项目的管理维护、扩展，也方便模块间的相互引用，资源共享。
- Slide 6: 策略一：按照功能模块拆分，比如：公共组件、商品模块、搜索模块、购物车模块、订单模块等。 策略二：按层拆分，比如：公共组件、实体类、控制层、业务层、数据访问层。 策略三：按照功能模块 + 层拆分。 分模块设计 - 策略 mall-common mall-goods mall-search mall-cart mall-order mall-common mal
- Slide 7: 分模块设计 - 实战
- Slide 8: 分模块开发 创建 maven 模块 tlias-pojo ，存放实体类。 创建 maven 模块 tlias-utils ，存放相关工具类。 分模块开发需要先针对模块功能进行设计，再进行编码。不会先将工程开发完毕，然后进行拆分。 注意：
- Slide 9: 什么是分模块设计 ? 将项目按照功能 模块 / 层 拆分成若干个子模块 为什么要分模块设计 ? 方便项目的管理维护、扩展，也方便模块间的相互 引 用，资源共享 注意事项 分模块设计需要先针对模块功能进行设计，再进行编码。不会先将工程开发完毕，然后进行拆分
- Slide 10: 分模块设计与开发 继承与聚合 私服

## 十一、配套代码索引

- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-autoconfigure\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-autoconfigure\src\main\java\com\aliyun\oss\AliyunOSSAutoConfiguration(1).java`
  - `@Configuration`
  - `public class AliyunOSSAutoConfiguration {`
  - `@Bean`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-autoconfigure\src\main\java\com\aliyun\oss\AliyunOSSAutoConfiguration.java`
  - `@Configuration`
  - `public class AliyunOSSAutoConfiguration {`
  - `@Bean`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-autoconfigure\src\main\java\com\aliyun\oss\AliyunOSSOperator.java`
  - `public class AliyunOSSOperator {`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-autoconfigure\src\main\java\com\aliyun\oss\AliyunOSSProperties.java`
  - `@ConfigurationProperties(prefix = "aliyun.oss")`
  - `public class AliyunOSSProperties {`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-starter\pom(1).xml`
  - `<dependency>`
  - `<dependency>`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\01. 自定义starter\aliyun-oss-spring-boot-starter\pom.xml`
  - `<dependency>`
  - `<dependency>`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\02. 完整的Tlias的代码\demo\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\02. 完整的Tlias的代码\demo\src\main\java\demo\DemoApplication.java`
  - `@SpringBootApplication`
  - `public class DemoApplication {`
- `ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\代码\02. 完整的Tlias的代码\demo\src\main\resources\application.properties`
