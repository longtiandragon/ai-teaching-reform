# SpringBoot AI 辅助教学课程资料索引

本目录由 `ppt/` 中的 SpringBoot 后端课程 PPT 和配套代码整理而来，可直接用于课堂讲义、AI 助教 RAG 知识库、练习反馈与教师备课。

## 课程总目标

- 建立从 Maven 工程、SpringBoot Web、数据库、MyBatis 到完整业务系统的后端开发路径。
- 让学生能围绕 Tlias 智能学习辅助系统完成接口、数据访问、认证、日志和统计功能。
- 将每讲资料拆成可检索的知识块，便于 AI 助教回答时引用课程来源。
- 服务教学改革 demo：学生练习、AI 反馈、教师学情分析形成闭环。

## 章节清单

1. [Maven 基础与 Java 项目构建](lesson-01-03-maven-basic.md)：让学生理解 Maven 的项目结构、依赖坐标、生命周期和测试打包流程，为后续 SpringBoot 工程做准备。
2. [SpringBoot Web 入门与分层解耦](lesson-02-04-springboot-web-basic.md)：从 HTTP 请求处理、Controller 入门、三层架构到 IOC/DI，建立 SpringBoot Web 开发第一条完整调用链。
3. [MySQL 数据库与 SQL 基础](lesson-03-05-mysql-sql.md)：讲授数据库、DBMS、SQL、表结构、约束、多表设计、查询和事务，为 Web 后端持久化建立基础。
4. [JDBC、连接池与 MyBatis 入门](lesson-04-06-jdbc-mybatis.md)：从 JDBC 规范和 PreparedStatement 出发，引出连接池、MyBatis Mapper、XML/注解 SQL 与 SpringBoot 整合。
5. [Tlias 部门管理与 RESTful 接口](lesson-05-07-dept-management.md)：围绕部门查询、新增、修改、删除实现前后端分离接口，建立统一响应、日志和接口文档意识。
6. [员工管理一：多表关系、多表查询与分页](lesson-06-08-emp-query.md)：讲授一对多、一对一、多对多关系、外键、连接查询，并完成员工列表分页和条件查询。
7. [员工管理二：新增员工、事务与文件上传](lesson-07-09-emp-save-upload-transaction.md)：围绕员工基本信息和工作经历批量保存，讲解主键回填、foreach 批量插入、声明式事务和文件上传。
8. [员工管理三：删除、修改、异常处理与统计](lesson-08-10-emp-update-exception-report.md)：完成批量删除、查询回显、员工修改、全局异常处理和统计报表接口，把 CRUD 推向可维护状态。
9. [班级与学员管理综合实战](lesson-09-11-project-practice.md)：以小组形式完成班级管理、学员管理、违纪处理和统计报表，训练需求分析、接口实现、联调和演示表达。
10. [登录认证、会话技术、JWT 与拦截器](lesson-10-12-login-auth.md)：从用户名密码登录引出登录标记、Cookie/Session、JWT、Filter/Interceptor 和统一登录校验。
11. [AOP 与操作日志](lesson-11-13-aop-log.md)：讲授连接点、切入点、通知、切面、目标对象和代理执行流程，并用自定义注解完成操作日志记录。
12. [SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级](lesson-12-14-springboot-principle.md)：收束 SpringBoot 工作原理，讲解配置优先级、Bean 作用域、第三方 Bean、自定义 starter、自动配置、多模块、继承聚合和私服。

## 建议教学路径

- 基础阶段：第 01-04 讲，完成 Maven、SpringBoot Web、MySQL、MyBatis。
- 实战阶段：第 05-10 讲，围绕 Tlias 完成部门、员工、班级、学员和登录认证。
- 进阶阶段：第 11-12 讲，完成 AOP 日志、SpringBoot 原理和 Maven 多模块。
- AI 教改融合：每讲都加入“AI 助教提示词”和“验收标准”，便于学生即时提问与教师复盘。

## RAG 使用说明

- 每个 Markdown 文件都保留了 PPT 来源、页码摘录和代码路径。
- 后端可以按文件切块导入，回答时引用 `docs/course-materials/lesson-xx-*.md`。
- 建议教师先用 `rag-seed.md` 快速初始化知识库，再按需上传单讲资料。
- 不包含任何真实 API Key 或敏感配置。
