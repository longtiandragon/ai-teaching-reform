# SpringBoot 课程 RAG 合并知识库


## 第01讲：Maven 基础与 Java 项目构建

来源文件：lesson-01-03-maven-basic.md
课程来源：ppt\03. 后端Web基础(Maven基础)\PPT\day03-Maven基础.pptx（70 页）
摘要：让学生理解 Maven 的项目结构、依赖坐标、生命周期和测试打包流程，为后续 SpringBoot 工程做准备。
学习目标：
- 解释 Maven 的作用：项目构建、统一结构、依赖管理
- 读懂 pom.xml 中 groupId、artifactId、version、dependency
- 能使用 compile、test、package 完成基础构建
- 能说明本地仓库、中央仓库、依赖传递的关系
课堂练习：
- 补全一个 Maven 项目的 pom.xml，添加 JUnit 依赖并编写一个 Service 单元测试。
- 学生需提交 pom.xml、测试类和 mvn test/package 的结果说明。

## 第02讲：SpringBoot Web 入门与分层解耦

来源文件：lesson-02-04-springboot-web-basic.md
课程来源：ppt\04. 后端Web基础(基础知识)\PPT\Day04-Web基础知识.pptx（70 页）
摘要：从 HTTP 请求处理、Controller 入门、三层架构到 IOC/DI，建立 SpringBoot Web 开发第一条完整调用链。
学习目标：
- 能创建 SpringBoot Web 工程并暴露 GET 接口
- 能区分静态资源、动态资源和 B/S 架构
- 能描述 Controller、Service、Dao 的职责
- 理解 IOC/DI 如何降低层间耦合
课堂练习：
- 基于资料中的用户列表案例，重构为 Controller-Service-Dao 三层，并说明每层职责。
- 提交接口路径、关键代码和一次请求的调用链说明。

## 第03讲：MySQL 数据库与 SQL 基础

来源文件：lesson-03-05-mysql-sql.md
课程来源：ppt\05. 后端Web基础(数据库)\PPT\Day05-数据库.pptx（67 页）
摘要：讲授数据库、DBMS、SQL、表结构、约束、多表设计、查询和事务，为 Web 后端持久化建立基础。
学习目标：
- 理解数据库、DBMS、SQL 的关系
- 掌握 DDL、DML、DQL、DCL 的基本使用
- 能设计带主键、唯一约束、外键的基础表结构
- 能解释事务 ACID 和提交/回滚
课堂练习：
- 设计 Tlias 部门与员工表，并编写部门列表、员工查询、删除部门前校验的 SQL。
- 提交建表 SQL、查询 SQL 和一致性说明。

## 第04讲：JDBC、连接池与 MyBatis 入门

来源文件：lesson-04-06-jdbc-mybatis.md
课程来源：ppt\06. 后端Web基础(java操作数据库)\PPT\Day06. 后端Web基础(java操作数据库).pptx（49 页）
摘要：从 JDBC 规范和 PreparedStatement 出发，引出连接池、MyBatis Mapper、XML/注解 SQL 与 SpringBoot 整合。
学习目标：
- 理解 JDBC 是 Java 操作关系型数据库的 API 规范
- 能使用 PreparedStatement 防止 SQL 注入
- 了解连接池降低连接创建成本
- 能编写 Mapper 接口完成基础 CRUD
课堂练习：
- 将 JDBC 登录查询改造成 MyBatis Mapper，并说明 SQL 注入防护点。
- 提交 Mapper 接口、SQL 映射和测试入口。

## 第05讲：Tlias 部门管理与 RESTful 接口

来源文件：lesson-05-07-dept-management.md
课程来源：ppt\07. 后端Web实战(部门管理)\PPT\Day07. 后端Web实战(部门管理).pptx（81 页）
摘要：围绕部门查询、新增、修改、删除实现前后端分离接口，建立统一响应、日志和接口文档意识。
学习目标：
- 能按 RESTful 风格设计部门资源接口
- 能实现 Result 统一响应结构
- 能完成部门 CRUD 的 Controller-Service-Mapper 调用链
- 能使用日志定位请求参数与执行结果
课堂练习：
- 完成部门管理 CRUD，并为每个接口写出请求方式、路径、参数、响应示例。
- 提交接口说明与关键代码。

## 第06讲：员工管理一：多表关系、多表查询与分页

来源文件：lesson-06-08-emp-query.md
课程来源：ppt\08. 后端Web实战(员工管理)\PPT\Day08. 后端Web实战(员工管理).pptx（64 页）
摘要：讲授一对多、一对一、多对多关系、外键、连接查询，并完成员工列表分页和条件查询。
学习目标：
- 能识别部门-员工的一对多关系
- 理解外键约束与级联风险
- 能编写员工条件分页查询
- 能返回 records、total、page、pageSize 等分页结果
课堂练习：
- 实现员工列表条件分页：姓名、性别、入职时间范围、部门。
- 提交 SQL/Mapper、返回结构和边界条件说明。

## 第07讲：员工管理二：新增员工、事务与文件上传

来源文件：lesson-07-09-emp-save-upload-transaction.md
课程来源：ppt\09. 后端Web实战(员工管理)\PPT\Day09. 后端Web实战(员工管理).pptx（52 页）
摘要：围绕员工基本信息和工作经历批量保存，讲解主键回填、foreach 批量插入、声明式事务和文件上传。
学习目标：
- 能使用 @Options 获取自增主键
- 能用 foreach 批量保存工作经历
- 能解释 @Transactional 的回滚条件
- 了解 MultipartFile 与对象存储/本地存储的边界
课堂练习：
- 实现新增员工接口：保存 emp 与 emp_expr，失败时整体回滚。
- 提交 Service 方法、Mapper 批量 SQL 和一次失败回滚说明。

## 第08讲：员工管理三：删除、修改、异常处理与统计

来源文件：lesson-08-10-emp-update-exception-report.md
课程来源：ppt\10. 后端Web实战(员工管理)\PPT\Day10. 后端Web实战(员工管理).pptx（35 页）
摘要：完成批量删除、查询回显、员工修改、全局异常处理和统计报表接口，把 CRUD 推向可维护状态。
学习目标：
- 能实现批量删除并清理关联工作经历
- 能完成修改前查询回显与提交更新
- 能使用 @RestControllerAdvice 统一异常响应
- 能编写员工性别/职位统计接口
课堂练习：
- 补全员工批量删除和全局异常处理，要求删除 emp 与 emp_expr 一致。
- 提交接口代码和异常响应示例。

## 第09讲：班级与学员管理综合实战

来源文件：lesson-09-11-project-practice.md
课程来源：ppt\11. 后端Web实战(项目实战)\PPT\Day11. 后端Web实战(项目实战).pptx（6 页）
摘要：以小组形式完成班级管理、学员管理、违纪处理和统计报表，训练需求分析、接口实现、联调和演示表达。
学习目标：
- 能根据接口文档拆分班级/学员功能
- 能完成 CRUD、违纪处理和统计接口
- 能进行前后端联调与演示
- 能复盘 Bug 原因和修复路径
课堂练习：
- 完成班级列表、新增、修改、删除与学员违纪处理，形成小组演示材料。
- 提交接口清单、核心实现和复盘记录。

## 第10讲：登录认证、会话技术、JWT 与拦截器

来源文件：lesson-10-12-login-auth.md
课程来源：ppt\12. 后端Web实战(登录认证)\PPT\12. 后端Web实战(登录认证).pptx（52 页）
摘要：从用户名密码登录引出登录标记、Cookie/Session、JWT、Filter/Interceptor 和统一登录校验。
学习目标：
- 能实现用户名密码登录查询
- 理解 Cookie、Session、JWT 的差异
- 能使用拦截器统一校验登录状态
- 能说明 Token 过期、篡改和敏感信息风险
课堂练习：
- 为 Tlias 系统补全登录认证：登录返回 JWT，其他接口通过拦截器校验。
- 提交登录接口、JWT 工具、拦截器配置和失败响应。

## 第11讲：AOP 与操作日志

来源文件：lesson-11-13-aop-log.md
课程来源：ppt\13. 后端Web进阶(AOP)\PPT\13. 后端Web进阶(AOP).pptx（34 页）
摘要：讲授连接点、切入点、通知、切面、目标对象和代理执行流程，并用自定义注解完成操作日志记录。

学习目标：
- 理解 AOP 五个核心概念（JoinPoint、PointCut、Advice、Aspect、Target）
- 能编写 @Aspect + @Around 统计耗时（见 RecordTimeAspect）
- 能用切入点表达式匹配业务方法（见 MyAspect5 的 12 种渐进写法）
- 能设计自定义注解记录操作日志（见 OperationLogAspect + @Log + OperateLog）

核心知识点摘要：
1. AOP 解决横切关注点——统计耗时不用在每个方法里写重复代码（RecordTimeAspect 对比原始做法）
2. 切入点表达式从精确到通配——MyAspect5 演示了 12 种 execution() 写法
3. 五种通知——MyAspect1 一个类写全 @Before/@Around/@After/@AfterReturning/@AfterThrowing
4. @Order 控制顺序——MyAspect2(@Order8)/3(@Order5)/4(@Order3) 演示栈式调用
5. JoinPoint API——MyAspect6 演示 getTarget()/getSignature().getName()/getArgs()
6. 生产级操作日志——OperationLogAspect 注入 OperateLogMapper 写数据库，CurrentHolder(ThreadLocal) 拿操作人

配套代码项目：
- springboot-aop-quickstart：RecordTimeAspect + MyAspect1~6（@Aspect 故意注释掉，讲师现场激活）
- tlias-web-management：OperationLogAspect + @Log + OperateLog + OperateLogMapper + CurrentHolder

课堂练习：
- 实现一个操作日志切面：标注 @Log 的方法执行后记录操作人、方法、参数、耗时和结果，写入数据库。
- 提交注解、切面类、Mapper 和日志示例。

## 第12讲：SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级

来源文件：lesson-12-14-springboot-principle.md
课程来源：ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web开发总结.pptx（6 页）；ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web进阶(Maven高级).pptx（35 页）；ppt\14. 后端Web进阶(SpringBoot原理&Maven高级)\PPT\14. 后端Web进阶(SpringBoot原理).pptx（36 页）
摘要：收束 SpringBoot 工作原理，讲解配置优先级、Bean 作用域、第三方 Bean、自定义 starter、自动配置、多模块、继承聚合和私服。
学习目标：
- 能说明 SpringBoot 配置优先级
- 理解 Bean 作用域和第三方 Bean 注册
- 能解释自动配置和自定义 starter 的基本结构
- 能进行 Maven 分模块、继承和聚合设计
课堂练习：
- 把单体 Tlias 工程拆成 pojo、utils、web-management 三个 Maven 模块，并说明依赖方向。
- 提交模块结构、父 pom、子模块 pom 和依赖说明。
