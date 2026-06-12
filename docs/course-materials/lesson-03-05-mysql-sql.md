# 第03讲：MySQL 数据库与 SQL 基础

> 课程来源：05. 后端Web基础(数据库)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

讲授数据库、DBMS、SQL、表结构、约束、多表设计、查询和事务，为 Web 后端持久化建立基础。

**本讲主线：** 数据库课要把“会写 SQL”升级为“会用表结构表达业务关系，并保证数据一致性”。

## 二、学习目标

- 理解数据库、DBMS、SQL 的关系
- 掌握 DDL、DML、DQL、DCL 的基本使用
- 能设计带主键、唯一约束、外键的基础表结构
- 能解释事务 ACID 和提交/回滚

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 数据库与 DBMS

**数据库（Database）**：存储数据的仓库，结构化的数据集合。

**DBMS（数据库管理系统）**：管理数据库的软件。常见的有 MySQL、Oracle、SQL Server、PostgreSQL。课程使用 **MySQL**。

**三者关系**：用户 → SQL 语句 → DBMS（MySQL） → 操作 → Database（具体库）→ 表 → 数据。

**MySQL 数据模型**：客户端连接 MySQL 服务器 → 一台服务器中有多个数据库（Database）→ 一个库中有多个表（Table）→ 表由行（Row/Record）和列（Column/Field）组成。

### 2. SQL 四大分类

| 分类 | 全称 | 用途 | 关键字 |
|------|------|------|--------|
| **DDL** | Data Definition Language | 定义数据库对象（库、表、字段） | `CREATE`, `ALTER`, `DROP` |
| **DML** | Data Manipulation Language | 操作数据（增删改） | `INSERT`, `UPDATE`, `DELETE` |
| **DQL** | Data Query Language | 查询数据 | `SELECT` |
| **DCL** | Data Control Language | 控制权限 | `GRANT`, `REVOKE` |

**DDL 示例 — 建表**：

```sql
CREATE TABLE dept (
    id        INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name      VARCHAR(20) NOT NULL UNIQUE COMMENT '部门名称',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    update_time DATETIME COMMENT '修改时间'
) COMMENT '部门表';
```

**DML 示例**：
```sql
INSERT INTO dept (name, create_time) VALUES ('教研部', NOW());
UPDATE dept SET name = '教学部' WHERE id = 1;
DELETE FROM dept WHERE id = 1;
```

**DQL 示例**：
```sql
SELECT id, name FROM dept WHERE name LIKE '%部%' ORDER BY id DESC;
```

### 3. 表结构与约束 — Tlias 系统的实际表设计

**约束类型**：

| 约束 | 关键字 | 含义 | 示例 |
|------|--------|------|------|
| 主键 | `PRIMARY KEY` | 唯一标识一行，非空唯一 | `id` |
| 非空 | `NOT NULL` | 字段不能为空 | `name` |
| 唯一 | `UNIQUE` | 字段值不能重复 | `name`（部门名不能重） |
| 默认值 | `DEFAULT` | 不传时的默认值 | `DEFAULT 1` |
| 外键 | `FOREIGN KEY` | 关联另一张表的主键 | `dept_id` 关联 `dept(id)` |

**外键约束示例**：
```sql
CREATE TABLE emp (
    id       INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name     VARCHAR(20) NOT NULL,
    dept_id  INT UNSIGNED,
    CONSTRAINT fk_emp_dept FOREIGN KEY (dept_id) REFERENCES dept(id)
);
```

**物理外键 vs 逻辑外键**：实际生产中很多团队不用物理外键（性能、分库分表问题），而是在应用层通过逻辑保证数据一致性。Tlias 课程初期可以先建外键帮助理解关系，后期再讨论取舍。

### 4. 事务与一致性

**事务**：一组 SQL 操作要么全部成功，要么全部失败（原子性）。

**ACID 四大特性**：

| 特性 | 含义 | 反例 |
|------|------|------|
| **原子性 (Atomicity)** | 一组操作不可分割 | 扣了钱但没加库存 |
| **一致性 (Consistency)** | 事务前后数据状态合法 | 余额变成负数 |
| **隔离性 (Isolation)** | 并发事务互不干扰 | 脏读、不可重复读 |
| **持久性 (Durability)** | 提交后数据永久保存 | 提交成功但重启后丢失 |

**SQL 中的事务操作**：
```sql
START TRANSACTION;           -- 开启事务
UPDATE account SET money = money - 100 WHERE id = 1;   -- 扣钱
UPDATE account SET money = money + 100 WHERE id = 2;   -- 加钱
COMMIT;                      -- 全部成功 → 提交
-- 或
ROLLBACK;                    -- 任何一步失败 → 回滚
```

**事务是后续 Spring `@Transactional` 的 SQL 层基础**——先理解 SQL 层的 COMMIT/ROLLBACK，再理解 Spring 如何用 AOP 自动管理事务边界。

## 五、课堂演示

- 创建 dept/emp 等业务表
- 演示 insert、update、delete、select
- 演示多表查询与事务失败回滚

## 六、课堂练习

- 设计 Tlias 部门与员工表，并编写部门列表、员工查询、删除部门前校验的 SQL。
- 提交建表 SQL、查询 SQL 和一致性说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 只会写单表查询，不会从业务关系推导表结构
- 误删有关联数据导致不一致
- 混淆事务和普通 SQL 执行顺序

## 九、AI 助教提示词

- 学生：我正在学习《MySQL 数据库与 SQL 基础》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《MySQL 数据库与 SQL 基础》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《MySQL 数据库与 SQL 基础》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\05. 后端Web基础(数据库)\PPT\Day05-数据库.pptx（67 页）
- Slide 1: Web 后端开发
- Slide 2: Dao 数据访问 Service 逻辑处理 Controller 接收请求、响应数据 数据库 不便维护、管理
- Slide 3: Web 后端开发 数据库
- Slide 4: 什么是数据库？ 数据库： D ata B ase （ DB ），是存储和管理数据的仓库。
- Slide 5: 什么是数据库？ 数据库： D ata B ase （ DB ），是存储和管理数据的仓库。 数据库
- Slide 6: 什么是数据库？ 数据库： D ata B ase （ DB ），是存储和管理数据的仓库。 数据库 数据库管理系统： D ata B ase M anagement S ystem( DBMS ) ，操纵和管理数据库的大型软件。 SQL ： S tructured Q uery L anguage ，操作关系型数据库的编程语言，定义了一套操作关系型数据库统一标
- Slide 7: 数据库产品 Oracle 收费的大型数据库， Oracle 公司的产品。 SQL Server MicroSoft 公司收费的中型的数据库。 C# 、 .net 等语言常使用。 PostgreSQL 开源免费中小型的数据库。 DB2 IBM 公司的大型收费数据库产品。 SQLite 嵌入式的微型数据库。如：作为 Android 内置数据库 MariaDB 开
- Slide 8: MySQL 概述 SQL 语句 多表设计 多表查询 事务
- Slide 9: MySQL 概述 SQL 语句
- Slide 10: MySQL 概述 01 安装 数据模型
- Slide 11: MySQL 安装 MySQL 官方提供了两种不同的版本： 商业版（ MySQL Enterprise Edition ） 收费，可以试用 30 天 官方提供技术支持 社区版（ MySQL Community Server ） 免费 MySQL 官方不提供技术支持 本课程采用的是 MySQL 的最新社区版 (MySQL Community Server 8.0
- Slide 12: MySQL 连接 语法： mysql –u 用户名 –p 密码 [ -h 数据库服务器 IP 地址 -P 端口号 ]
- Slide 13: MySQL- 企业开发使用方式
- Slide 14: MySQL 安装 根据文档操作 MySQL 连接 mysql -h xxx -P xxx -u xxx -p xxx

## 十一、配套代码索引

- `ppt\05. 后端Web基础(数据库)\代码\SQL脚本.sql`
  - `select database();`
  - `create table user(`
  - `create table user(`
