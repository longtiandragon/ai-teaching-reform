# 第07讲：员工管理二：新增员工、事务与文件上传

> 课程来源：09. 后端Web实战(员工管理)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

围绕员工基本信息和工作经历批量保存，讲解主键回填、foreach 批量插入、声明式事务和文件上传。

**本讲主线：** 一个员工新增操作可能写多张表，事务边界必须覆盖完整业务动作。

## 二、学习目标

- 能使用 @Options 获取自增主键
- 能用 foreach 批量保存工作经历
- 能解释 @Transactional 的回滚条件
- 了解 MultipartFile 与对象存储/本地存储的边界

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. 新增业务链 — 农博项目的 insert 模式

农博项目中新增一条农产品记录的完整流程：

```java
// 来源: 农博项目/.../impl/NbFarmProduceServiceImpl.java
@Service
public class NbFarmProduceServiceImpl implements INbFarmProduceService {

    @Autowired
    private NbFarmProduceMapper produceMapper;

    @Override
    public int insert(NbFarmProduce produce) {
        // 1. UUID 生成主键（农博用 String 类型 ID）
        if (produce.getId() == null || produce.getId().isEmpty()) {
            produce.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        // 2. 执行 XML INSERT
        return produceMapper.insert(produce);
    }
}
```

**农博 vs Tlias 教学项目的 ID 策略**：

| | 农博项目 | Tlias PPT 教学 |
|---|---|---|
| ID 类型 | `String` | `Integer` / `Long` |
| 生成方式 | `UUID.randomUUID()` | 数据库自增 `AUTO_INCREMENT` |
| 主键回填 | 不需要（插入前就生成了） | `@Options(useGeneratedKeys = true)` |

### 2. foreach 批量操作 — 农博项目 XML 中的 `deleteBatch`

```xml
<!-- 来源: 农博项目/mapper/NbFarmProduceMapper.xml -->
<delete id="deleteBatch">
    DELETE FROM nb_farm_produce WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</delete>
```

**Controller 中调用**：

```java
// 来源: 农博项目/NbFarmProduceController.java
@DeleteMapping("/batch")
public Result<Void> deleteBatch(@RequestBody String[] ids) {
    produceService.deleteBatch(ids);
    return Result.success("Deleted successfully");
}
```

### 3. 声明式事务 — `@Transactional`

农博项目中使用与所有 Spring 项目一致的声明式事务。在需要保证数据一致性的 Service 方法上加 `@Transactional`：

```java
@Transactional
public int insert(NbFarmProduce produce) {
    // 如果这里有多步操作（比如插入主表+子表），失败会整体回滚
    produceMapper.insert(produce);
    return 1;
}
```

**事务失效的常见场景**（适用于所有 SpringBoot 项目）：
- 加在非 public 方法上
- 同类内部调用（`this.method()` 不经过代理）
- 异常被 catch 吞掉未继续抛出
- 数据库引擎不支持事务（MyISAM）

### 4. 文件上传 — 农博项目的 `FileUploadConfig`

```java
// 来源: 农博项目/.../config/FileUploadConfig.java
@Configuration
public class FileUploadConfig implements WebMvcConfigurer {

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.access.prefix:/uploads}")
    private String accessPrefix;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path uploadRoot = resolveUploadRoot();
        registry.addResourceHandler(accessPrefix + "/**")
                .addResourceLocations(uploadRoot.toUri().toString());
    }
}
```

**配置项**：`file.upload.path`（上传路径）、`file.access.prefix`（访问 URL 前缀）。文件通过静态资源映射直接访问，无需额外编写下载接口。

## 五、课堂演示

- 新增员工基本信息后回填 id
- 批量插入 emp_expr
- 故意制造异常观察事务回滚
- 演示头像上传接口返回访问地址

## 六、课堂练习

- 实现新增员工接口：保存 emp 与 emp_expr，失败时整体回滚。
- 提交 Service 方法、Mapper 批量 SQL 和一次失败回滚说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 事务加在 Controller 或 private 方法上无效
- 只保存主表不保存子表
- 上传文件名冲突或未限制类型

## 九、AI 助教提示词

- 学生：我正在学习《员工管理二：新增员工、事务与文件上传》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《员工管理二：新增员工、事务与文件上传》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《员工管理二：新增员工、事务与文件上传》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\09. 后端Web实战(员工管理)\PPT\Day09. 后端Web实战(员工管理).pptx（52 页）
- Slide 1: Web 后端开发 Tlias 系统 - 员工管理
- Slide 2: 需求 新增员工 事务管理 文件上传
- Slide 3: 新增员工 事务管理 文件上传
- Slide 4: 新增员工 01
- Slide 5: 需求 员工基本信息（表： emp ） 员工工作经历信息（表： emp_expr ）
- Slide 6: 新增员工 - 思路 Controller 接收请求参数 ( 员工信息 ) 调用 Service 方法 响应结果 Service 保存员工基本信息 批量保存员工的工作经历信息 Mapper SQL: insert into emp(...) values (...); insert into emp_expr(...) values(...),(...); 员
- Slide 7: 新增员工 - 保存员工基本信息 @PostMapping public Result save ( @RequestBody Emp emp){ log .info( " 请求参数 emp: {}" , emp); empService .save(emp); return Result . success (); } EmpController publi
- Slide 8: 新增员工 - 批量保存工作经历 insert into emp_expr(...) values (?,?,?,?,?) insert into emp_expr(...) values (?,?,?,?,?),(?,?,?,?,?) insert into emp_expr(...) values (?,?,?,?,?),(?,?,?,?,?),(?,?,
- Slide 9: 新增员工 - 批量保存工作经历 insert into emp_expr(...) values (?,?,?,?,?),(?,?,?,?,?),(?,?,?,?,?) List<EmpExpr> 动态 SQL ： <foreach> public void insertBatch ( List < EmpExpr > exprList); EmpExprM
- Slide 10: 在插入数据之后，如何获取到主键值 ？ @Options (useGeneratedKeys = true , keyProperty = "id" ) 2. <foreach> 动态 SQL 标签的作用 ? 其中属性的含义 ? 作用：遍历集合 / 数组 属性： collection ： 集合名称 item ： 集合遍历出来的元素 / 项 separator 
- Slide 11: 保存员工的基本信息成功了，而保存工作经历失败了，是否 OK ？ 不可以 ; 因为这属于一个业务操作，如果保存员工信息成功了，保存工作经历信息失败了，就会造成数据库数据的不完整、不一致。 emp emp_expr 事务管理
- Slide 12: 新增员工 事务管理 文件上传
- Slide 13: 介绍 & 操作 Spring 事务管理 四大特性 事务管理 02
- Slide 14: 概念： 事务 是一组操作的集合，它是一个不可分割的工作单位。事务会把所有的操作作为一个整体一起向系统提交或撤销操作请求，即这些操作 要么同时成功，要么同时失败 。 介绍 -- 1. 保存员工基本信息 insert into emp values ( 39 , 'Tom' , '123456' , ' 汤姆 ' , 1 , '13300001111' , 1 

## 十一、配套代码索引

- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\EmpController.java`
  - `@RestController`
  - `public class EmpController {`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\controller\UploadController.java`
  - `@RestController`
  - `public class UploadController {`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\DeptMapper.java`
  - `@Mapper`
  - `public interface DeptMapper {`
  - `@Select("select id, name, create_time, update_time from dept order by update_time desc")`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpExprMapper.java`
  - `@Mapper`
  - `public interface EmpExprMapper {`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpLogMapper.java`
  - `@Mapper`
  - `public interface EmpLogMapper {`
  - `@Insert("insert into emp_log (operate_time, info) values (#{operateTime}, #{info})")`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\mapper\EmpMapper.java`
  - `@Mapper`
  - `public interface EmpMapper {`
  - `@Insert("insert into emp(username, name, gender, phone, job, salary, image, entry_date, dept_id, create_time, update_time)" +`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\pojo\Dept.java`
  - `public class Dept {`
- `ppt\09. 后端Web实战(员工管理)\代码\tlias-web-management\src\main\java\com\itheima\pojo\Emp.java`
  - `public class Emp {`
