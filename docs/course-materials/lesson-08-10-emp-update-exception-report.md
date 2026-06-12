# 第08讲：员工管理三：删除、修改、异常处理与统计

> 课程来源：10. 后端Web实战(员工管理)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

完成批量删除、查询回显、员工修改、全局异常处理和统计报表接口，把 CRUD 推向可维护状态。

**本讲主线：** 成熟的 CRUD 不只是增删改查，还包括批量操作、异常可解释和统计结果可视化。

## 二、学习目标

- 能实现批量删除并清理关联工作经历
- 能完成修改前查询回显与提交更新
- 能使用 @RestControllerAdvice 统一异常响应
- 能编写员工性别/职位统计接口

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 全局异常处理 — 从 `GlobalExceptionHandler` 看三层处理

**问题驱动**：如果不做统一异常处理，Controller 中每个方法都要 try-catch，代码重复；而且异常信息直接暴露堆栈给前端不安全也不友好。

**`@RestControllerAdvice` 解决方案**：

```java
// 来源: tlias-web-management/.../exception/GlobalExceptionHandler.java
@Slf4j
@RestControllerAdvice    // = @ControllerAdvice + @ResponseBody
public class GlobalExceptionHandler {

    // 兜底异常 — 捕获所有未处理的 Exception
    @ExceptionHandler
    public Result handleException(Exception e) {
        log.error("程序出错啦~", e);
        return Result.error("出错啦, 请联系管理员~");  // 不暴露堆栈给前端
    }

    // 特定异常: 唯一键冲突 — 解析 MySQL 错误信息返回可读提示
    @ExceptionHandler
    public Result handleDuplicateKeyException(DuplicateKeyException e) {
        log.error("程序出错啦~", e);
        String message = e.getMessage();
        int i = message.indexOf("Duplicate entry");
        String errMsg = message.substring(i);
        String[] arr = errMsg.split(" ");
        return Result.error(arr[2] + " 已存在");  // 比如: "教研部 已存在"
    }

    // 业务异常 — 直接返回业务层定义的错误信息
    @ExceptionHandler
    public Result handleBuinessException(BusinessException businessException) {
        log.error("服务器异常", businessException);
        return Result.error(businessException.getMessage());
    }
}
```

**异常分层处理策略**：

| 异常类型 | 处理方式 | 示例 |
|---------|---------|------|
| `BusinessException`（自定义） | 返回业务错误信息给前端 | "部门下有员工，不能删除" |
| `DuplicateKeyException`（数据库） | 解析为可读提示 | "教研部 已存在" |
| `Exception`（兜底） | 统一返回模糊提示，写详细日志 | "出错啦, 请联系管理员~" |

**为什么要区分三层处理**：不让数据库异常原文暴露给前端（安全），但要给用户可操作的提示（体验），开发者通过日志定位问题。

**`@RestControllerAdvice` 工作原理**：Spring MVC 的异常处理机制。当 Controller 抛出异常时，框架查找匹配的 `@ExceptionHandler` 方法，按异常类型匹配（优先匹配最具体的子类），将其返回值作为响应。

### 2. 批量删除与关联数据清理

批量删除的核心问题：删除员工时要同时清理关联的工作经历（`emp_expr` 表），否则出现孤儿数据。

**接口示例**：`DELETE /emps?ids=1,2,3` — 接收逗号分隔的 ID 列表，遍历删除每个员工及其关联数据。

**关键注意**：先删子表再删主表（或使用事务保证一致性）；参数解析注意空值和非法值。

### 3. 查询回显与修改

修改流程：`GET /emps/{id}` 查询回显 → 前端展示表单 → 用户修改 → `PUT /emps` 提交更新。

回显接口负责把现有数据原样返回填充表单；更新接口需要区分哪些字段可以被修改（工号不可改、姓名可改等）。

### 4. 统计报表接口

将 SQL 聚合查询结果（GROUP BY + COUNT）封装为图表数据：`[{name: "职位名", value: 人数}]`，前端用 ECharts 渲染。重点在于 Controller 返回的数据结构要匹配前端图表组件的格式约定。

## 五、课堂演示

- DELETE /emps?ids=1,2,3
- GET /emps/{id} 查询回显
- PUT /emps 修改员工
- 统计员工职位分布并返回图表数据

## 六、课堂练习

- 补全员工批量删除和全局异常处理，要求删除 emp 与 emp_expr 一致。
- 提交接口代码和异常响应示例。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 数组/集合参数绑定失败
- 关联数据未删除
- 异常信息直接暴露堆栈

## 九、AI 助教提示词

- 学生：我正在学习《员工管理三：删除、修改、异常处理与统计》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《员工管理三：删除、修改、异常处理与统计》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《员工管理三：删除、修改、异常处理与统计》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\10. 后端Web实战(员工管理)\PPT\Day10. 后端Web实战(员工管理).pptx（35 页）
- Slide 1: Web 后端开发 Tlias 系统 - 员工管理
- Slide 2: 需求 删除员工 修改员工 异常处理 员工信息统计
- Slide 3: 删除员工 修改员工 异常处理 员工信息统计
- Slide 4: 删除员工 01
- Slide 5: 需求分析 其实，删除单条数据也是一种特殊的批量删除，所以，删除员工的功能，我们只需要开发一个接口就可以了。 根据 ID 删除单个员工信息 根据 ID 批量 删除员工信息
- Slide 6: 删除员工 Controller 接收请求参数 (ID 值 ) 调用 Service 方法 响应结果 Service 批量删除员工基本信息 批量删除员工的工作经历信息 Mapper SQL: delete emp where id in (?,?,?); delete emp_expr where emp_id in(?,?,?);
- Slide 7: 删除员工 -Controller 接收请求参数 @DeleteMapping public Result delete (Integer[] ids){ log .info( " 根据 id 批量删除员工 :{} " , ids); return Result . success (); } EmpController 方式一：在 Controller 方法
- Slide 8: 删除员工 -Service&Mapper @Transactional (rollbackFor = { Exception . class }) public void deleteByIds ( List < Integer > ids) { //1. 根据 ID 删除员工基本信息 empMapper .deleteByIds(ids); //2. 根据
- Slide 9: 删除员工 修改员工 异常处理 员工信息统计
- Slide 10: 修改员工 02
- Slide 11: 需求分析 查询回显 修改数据
- Slide 12: 修改员工 查询回显 修改数据 02
- Slide 13: 查询回显 员工基本信息（表： emp ） 员工工作经历信息（表： emp_expr ） Controller 接收请求参数 (ID 值 ) 调用 Service 方法 响应结果 Service 调用 mapper 查询员工详细信息 ( 基本信息、工作经历信息 ) Mapper SQL: select ... from emp e left join emp_
- Slide 17: 需求分析 Controller 接收请求参数 调用 Service 方法 响应结果 Service 根据 ID 修改员工的基本信息 根据 ID 修改工作经历信息 Mapper SQL: update emp set .... delete emp_expr where... insert into emp_expr... （ 先删除再添加 ）

## 十一、配套代码索引

- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\EmpController.java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\ReportController.java`
  - `@RestController`
  - `public class ReportController {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\UploadController.java`
  - `@RestController`
  - `public class UploadController {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\exception\GlobalExceptionHandler.java`
  - `@RestControllerAdvice`
  - `public class GlobalExceptionHandler {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\DeptMapper.java`
  - `@Mapper`
  - `public interface DeptMapper {`
  - `@Select("select id, name, create_time, update_time from dept order by update_time desc")`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpExprMapper.java`
  - `@Mapper`
  - `public interface EmpExprMapper {`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpLogMapper.java`
  - `@Mapper`
  - `public interface EmpLogMapper {`
  - `@Insert("insert into emp_log (operate_time, info) values (#{operateTime}, #{info})")`
- `ppt\10. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpMapper.java`
  - `@Mapper`
  - `public interface EmpMapper {`
  - `@Insert("insert into emp(username, name, gender, phone, job, salary, image, entry_date, dept_id, create_time, update_time)" +`
