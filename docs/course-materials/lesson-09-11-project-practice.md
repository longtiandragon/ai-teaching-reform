# 第09讲：班级与学员管理综合实战

> 课程来源：11. 后端Web实战(项目实战)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

以小组形式完成班级管理、学员管理、违纪处理和统计报表，训练需求分析、接口实现、联调和演示表达。

**本讲主线：** 项目实战的关键成果不是“照着写完”，而是能讲清实现思路、典型 Bug 和解决方案。

## 二、学习目标

- 能根据接口文档拆分班级/学员功能
- 能完成 CRUD、违纪处理和统计接口
- 能进行前后端联调与演示
- 能复盘 Bug 原因和修复路径

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 需求拆解 — 从功能列表到接口

综合实战要求学生完成班级管理（Clazz）、学员管理（Student）、违纪处理、统计报表四个模块。拿到需求后第一步不是写代码，而是拆接口：

**以班级管理为例**：

| HTTP 方法 | 路径 | 说明 | 类比（部门管理） |
|-----------|------|------|:---:|
| GET | `/clazzs` | 班级列表+条件分页 | 同 `GET /depts` |
| POST | `/clazzs` | 新增班级 | 同 `POST /depts` |
| GET | `/clazzs/{id}` | 查询回显 | 同 `GET /depts/{id}` |
| PUT | `/clazzs` | 修改班级 | 同 `PUT /depts` |
| DELETE | `/clazzs/{id}` | 删除班级 | 同 `DELETE /depts` |

学员管理同理。学生应能独立完成从部门管理的 CRUD 模式迁移到新实体。

### 2. 接口清单 — 前后端联调的契约

接口清单（Swagger/接口文档）必须包含：请求方式、路径、请求参数（QueryString/Body）、响应结构（code/data 格式）。前后端双方都按这个契约开发，联调时才不会因为字段名不一致而返工。

**接口示例 — 违纪处理**：
```
POST /students/{id}/violation
请求体: { "type": "迟到", "description": "上课迟到15分钟", "points": 2 }
响应:   { "code": 1, "msg": "success", "data": null }
```

### 3. 前后端联调 — 从 Mock 数据到真实接口

联调步骤：先确保后端接口用 Postman/Apifox 测试通过 → 前端连接真实后端替换 Mock 数据 → 检查字段名匹配 → 处理边界情况（空列表、网络错误等）。

常见联调问题：状态码 200 但 code=0（业务失败）；字段名大小写不一致（后端 `className` 前端 `classname`）；时间格式不一致。

### 4. 小组演示与复盘

综合实战的标准产出：
- **代码**：可运行的 CRUD + 违纪 + 统计接口
- **演示脚本**：每人负责一块，展示功能、说清调用链
- **Bug 复盘**：记下开发中遇到的实际问题 + 怎么解决的（不是"改好了"三个字敷衍）

演示不是只跑通接口，要能说明每层的职责和关键决策（为什么这么设计表、为什么 Service 加事务）。

## 五、课堂演示

- 小组拆分班级管理和学员管理任务
- 按接口文档开发并联调
- 准备演示脚本：功能、代码、Bug、改进

## 六、课堂练习

- 完成班级列表、新增、修改、删除与学员违纪处理，形成小组演示材料。
- 提交接口清单、核心实现和复盘记录。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 只做功能不写接口说明
- 联调时状态码和字段名不一致
- 无法复盘问题，只说“改好了”

## 九、AI 助教提示词

- 学生：我正在学习《班级与学员管理综合实战》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《班级与学员管理综合实战》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《班级与学员管理综合实战》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\11. 后端Web实战(项目实战)\PPT\Day11. 后端Web实战(项目实战).pptx（6 页）
- Slide 1: Web 后端开发 项目实战
- Slide 2: 需求
- Slide 3: 班级管理：班级列表查询、删除班级、添加班级、修改班级。 学员管理：学员列表查询、删除学员、添加学员、修改学员、违纪处理。 数据统计：班级人数统计、学员学历统计。 注意：所有的功能全部严格，根据接口文档进行开发，并进行前后端联调。 需求
- Slide 4: 最终效果
- Slide 5: 暂停视频，完成所有实战需求 全部完成后，再继续往下学习 ~
- Slide 6: 以小组为单位，进行实战，每一个都需要完成实战需求。出现问题，务必自己先思考，然后组内讨论交流解决。 每一个组，需要选一名组员上来演示所完成的系统功能。 演示的时候，可以介绍一下，自己在实现这个功能的过程中，你自己的实现思路和方案。 自己实现这一块功能过程中遇到的典型的 Bug ，产生 Bug 的原因，以及解决方案。 实战说明

## 十一、配套代码索引

- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\ClazzController.java`
  - `@RestController`
  - `public class ClazzController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\EmpController.java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\ReportController.java`
  - `@RestController`
  - `public class ReportController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\StudentController.java`
  - `@RestController`
  - `public class StudentController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\controller\UploadController.java`
  - `@RestController`
  - `public class UploadController {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\exception\BusinessException.java`
  - `public class BusinessException extends RuntimeException{`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\exception\GlobalExceptionHandler.java`
  - `@RestControllerAdvice`
  - `public class GlobalExceptionHandler {`
- `ppt\11. 后端Web实战(项目实战)\代码\tlias-web-management\src\main\java\com\itheima\mapper\ClazzMapper.java`
  - `@Mapper`
  - `public interface ClazzMapper {`
  - `@Insert("insert into clazz VALUES (null,#{name},#{room},#{beginDate},#{endDate},#{masterId}, #{subject},#{createTime},#{updateTime})")`
