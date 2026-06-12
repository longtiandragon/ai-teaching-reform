# 第06讲：员工管理一：多表关系、多表查询与分页

> 课程来源：08. 后端Web实战(员工管理)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

讲授一对多、一对一、多对多关系、外键、连接查询，并完成员工列表分页和条件查询。

**本讲主线：** 员工列表不是简单 select，而是多表关系、动态条件和分页结果结构的综合训练。

## 二、学习目标

- 能识别部门-员工的一对多关系
- 理解外键约束与级联风险
- 能编写员工条件分页查询
- 能返回 records、total、page、pageSize 等分页结果

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 多表关系

| 关系类型 | 举例 | 实现方式 |
|---------|------|---------|
| **一对多** | 一个分类下有多个农产品 | "多"的表加外键：`catgory` 字段关联 |
| **一对一** | 一个用户对应一份详细信息 | 任意一方加唯一外键 |
| **多对多** | 一个角色关联多个权限 | 中间表 |

**设计原则**：先分析业务实体 → 再看实体间关系 → 最后确定外键位置或中间表。

### 2. 连接查询

```sql
-- INNER JOIN: 查询农产品及其分类
SELECT p.title, p.catgory FROM nb_farm_produce p
INNER JOIN nb_category c ON p.catgory_id = c.id;

-- LEFT JOIN: 包括没有农产品的分类（统计为0）
SELECT c.name, COUNT(p.id) AS 数量 FROM nb_category c
LEFT JOIN nb_farm_produce p ON p.catgory_id = c.id
GROUP BY c.id, c.name;
```

### 3. 分页查询 — 农博项目的 `PageQuery` + `LIMIT #{offset}` 模式

**农博项目的分页方式**：不用 PageHelper，而是用一个 `PageQuery` 对象 + XML 中的 `LIMIT #{offset}, #{pageSize}`：

```java
// 来源: 农博项目/.../common/PageQuery.java
@Data
public class PageQuery {
    private Integer pageNum = 1;     // 当前页码，默认1
    private Integer pageSize = 10;   // 每页条数，默认10

    public Integer getOffset() {     // 计算起始行
        return (pageNum - 1) * pageSize;
    }
}
```

**Controller 中使用**：

```java
// 来源: 农博项目/.../controller/NbFarmProduceController.java
@GetMapping("/list")
public Result<NbFarmProduce> list(PageQuery pageQuery,
                                  @RequestParam(required = false) String title) {
    Map<String, Object> params = new HashMap<>();
    if (pageQuery != null) {
        params.put("offset", pageQuery.getOffset());    // LIMIT 起始行
        params.put("pageSize", pageQuery.getPageSize());// 每页条数
    }
    params.put("title", title);
    return produceService.selectList(params);
}
```

**XML 中使用**：

```xml
<select id="selectList" resultMap="BaseResultMap">
    SELECT * FROM nb_farm_produce
    <where>
        <if test="title != null and title != ''">
            AND title LIKE CONCAT('%', #{title}, '%')
        </if>
    </where>
    ORDER BY created_time DESC
    <if test="offset != null and pageSize != null">
        LIMIT #{offset}, #{pageSize}
    </if>
</select>
```

**Service 中组装分页结果**：

```java
// 来源: 农博项目/.../impl/NbFarmProduceServiceImpl.java
public Result<NbFarmProduce> selectList(Map<String, Object> params) {
    List<NbFarmProduce> list = mapper.selectList(params);   // 查询列表
    Long total = mapper.selectCount(params);                 // 查询总数
    Result result = Result.success();
    result.setRows(list);                                    // 设置列表
    result.setTotal(total);                                  // 设置总数
    result.buildPageData();                                  // 转换成 {records, total}
    return result;
}
```

**分页响应格式**（农博风格）：

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "records": [ {农产对象...} ],
    "total": 25
  }
}
```

**PageHelper vs 农博 PageQuery**：

| | PageHelper（PPT 教学） | PageQuery（农博项目） |
|---|---|---|
| 方式 | `PageHelper.startPage()` + 强转 | `getOffset()` + XML LIMIT |
| SQL 感知 | 透明（框架自动加 LIMIT） | 显式（在 XML 中写 LIMIT） |
| 依赖 | 需要 MyBatis PageHelper 插件 | 零额外依赖 |
| 学习价值 | 方便但不懂原理 | 帮助理解分页 SQL 本质 |

## 五、课堂演示

- 创建 dept、emp、emp_expr 等表关系
- 演示 inner join、left join
- 使用 PageHelper 或 limit 完成员工分页

## 六、课堂练习

- 实现员工列表条件分页：姓名、性别、入职时间范围、部门。
- 提交 SQL/Mapper、返回结构和边界条件说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 连接查询字段冲突或别名缺失
- 分页 total 与 records 不一致
- 动态 SQL 空条件拼接错误

## 九、AI 助教提示词

- 学生：我正在学习《员工管理一：多表关系、多表查询与分页》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《员工管理一：多表关系、多表查询与分页》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《员工管理一：多表关系、多表查询与分页》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\08. 后端Web实战(员工管理)\PPT\Day08. 后端Web实战(员工管理).pptx（64 页）
- Slide 1: Web 后端开发 Tlias 系统 - 员工管理
- Slide 2: 需求 多表关系 多表查询 员工列表查询
- Slide 3: 多表关系 多表查询 员工列表查询
- Slide 4: 多表关系 01
- Slide 5: 概述 项目开发中，在进行数据库表结构设计时，会根据业务需求及业务模块之间的关系，分析并设计表结构。由于业务之间相互关联，所以各个表结构之间也存在着各种联系。 多表关系分为三种： 一对多 ( 多对一 ) 一对一 多对多
- Slide 6: 多表关系 一对多（多对一） 一对一 多对多 案例 01
- Slide 7: 一对多 场景：部门与员工的关系 （一个部门下有多个员工）。
- Slide 8: 一对多 场景：部门与员工的关系 （一个部门下有多个员工）。 create table dept ( id int unsigned primary key auto_increment comment 'ID' , name varchar ( 10 ) not null unique comment ' 部门名称 ' , create_time datet
- Slide 9: 一对多 场景：部门与员工的关系 （一个部门下有多个员工）。 一 多 父 表 子 表 一对多的关系如何实现 ? 在数据库表中多的一方，添加字段，来关联一的一方的主键。
- Slide 10: 数据库中如何体现一对多的表关系？ 需要在多的一方添加字段，关联一的一方的主键
- Slide 11: 多表问题分析 现象 ： 部门数据可以直接删除，然而还有部分员工归属于该部门下，此时就出现了数据的不完整、不一致问题 。 原因： 目前上述的两张表，在数据库层面，并未建立关联，所以是无法保证数据的一致性和完整性的 。 解决方案：外键约束 。
- Slide 12: 外键约束 可以在创建表时 或 表结构创建完成后，为字段添加外键约束。 具体语法如下： -- 创建表时指定 create table 表名 ( 字段名 数据类型 , ... [ constraint ] [ 外键名称 ] foreign key ( 外键字段名 ) references 主表 ( 字段名 ) ); 创建表时 , 添加外键约束 -- 建完表后，添
- Slide 22: 根据页面原型及需求文档分析并设计表结构 需求：请根据资料中提供的页面原型， 设计 员工模块 涉及到的表结构 。 步骤： 阅读页面原型及需求文档，分析各个模块涉及到的表结构，及表结构之间的关系。 根据页面原型及需求文档，分析各个表结构中具体的字段及约束。
- Slide 30: 外连接 外连接分为左外连接和右外连接。具体语法为： A ∩ B A -- 1. 左外 连接 ( 常见 ) select 字段列表 from 表 1 left [ outer ] join 表 2 on 连接 条件 ...; -- 2. 右外连接 select 字段列表 from 表 1 right [ outer ] join 表 2 on 连接 条件 ..

## 十一、配套代码索引

- `ppt\08. 后端Web实战(员工管理)\代码\01. 多表设计&多表查询\多表关系.sql`
  - `CREATE TABLE dept (`
  - `INSERT INTO dept VALUES (1,'学工部','2023-09-25 09:47:40','2023-09-25 09:47:40'),`
  - `create table emp(`
- `ppt\08. 后端Web实战(员工管理)\代码\01. 多表设计&多表查询\多表查询.sql`
  - `create table dept(`
  - `insert into dept (id, name, create_time, update_time) values`
  - `create table emp(`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\controller\DeptController(1).java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\controller\EmpController(1).java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\controller\EmpController.java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\mapper\DeptMapper.java`
  - `@Mapper // 标识当前接口是一个Mybatis的Mapper接口 ---> 实现类对象 --> IOC容器`
  - `public interface DeptMapper {`
  - `//@Select("SELECT id, name, create_time, update_time FROM dept ORDER BY update_time DESC")`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\mapper\EmpMapper.java`
  - `@Mapper`
  - `public interface EmpMapper {`
  - `@Select("select emp.*, dept.name as dept_name from emp left join dept on emp.dept_id = dept.id limit #{start},#{pageSize}")`
- `ppt\08. 后端Web实战(员工管理)\代码\02. 原始分页查询代码实现\tlias-web-management\src\main\java\com\itheima\pojo\Dept.java`
  - `public class Dept {`
