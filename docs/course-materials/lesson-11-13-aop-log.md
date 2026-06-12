# 第11讲：AOP 与操作日志

> 课程来源：13. 后端Web进阶(AOP)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

讲授连接点、切入点、通知、切面、目标对象和代理执行流程，并用自定义注解完成操作日志记录。

**本讲主线：** AOP 的教学重点是横切逻辑如何无侵入地织入业务方法。

## 二、学习目标

- 理解 AOP 五个核心概念
- 能编写 @Aspect + @Around 统计耗时
- 能用切入点表达式匹配业务方法
- 能设计自定义注解记录操作日志

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. AOP 解决什么问题 — 从 `RecordTimeAspect` 看

你的 PPT Slide 2-3 给出了场景：Tlias 系统中，如果要统计每个业务方法的执行耗时——

**原始做法**（每个方法里都写一遍）：

```java
public List<Dept> list() {
    long beginTime = System.currentTimeMillis();
    List<Dept> deptList = deptMapper.list();
    long endTime = System.currentTimeMillis();
    // ...5 个方法写 5 遍
}
```

**AOP 做法**（写一次，自动织入所有目标方法）：

```java
// 来源: springboot-aop-quickstart/.../aop/RecordTimeAspect.java
@Slf4j
//@Aspect // ← 故意注释掉！讲师现场取消注释即可激活
@Component
public class RecordTimeAspect {

    @Around("execution(* com.itheima.service.impl.*.*(..))")
    public Object recordTime(ProceedingJoinPoint pjp) throws Throwable {
        long begin = System.currentTimeMillis();           // 1. 记录方法运行的开始时间
        Object result = pjp.proceed();                     // 2. 执行原始的方法
        long end = System.currentTimeMillis();             // 3. 记录方法运行的结束时间
        log.info("方法 {} 执行耗时: {}ms", pjp.getSignature(), end - begin);
        return result;
    }
}
```

**三步走模式**：`记录开始 → proceed() → 记录结束并输出`。这就是 AOP 中所有环绕通知的标准写法。

**AOP 的典型应用（PPT Slide 8 原文）**：

| 场景 | 在 Tlias 中的落地 |
|------|------------------|
| 记录系统的操作日志 | `OperationLogAspect` → `operate_log` 表 |
| 事务管理 | Spring `@Transactional` 底层就是 AOP |
| 权限控制 | 进入方法前校验角色 |

**AOP 优势（PPT Slide 3）**：减少重复代码、代码无侵入、提高开发效率、维护方便。AOP 是一种思想，Spring 框架对其做了实现。

---

### 2. 五个核心概念与切入点表达式 — 从 `MyAspect5` 渐进教学看

**PPT Slide 10 的定义**：

> - **连接点（JoinPoint）**：可以被 AOP 控制的方法（暗含方法执行时的相关信息）
> - **通知（Advice）**：指那些重复的逻辑，也就是共性功能（最终体现为一个方法）
> - **切入点（PointCut）**：匹配连接点的条件，通知仅会在切入点方法执行时被应用
> - **切面（Aspect）**：描述通知与切入点的对应关系（通知 + 切入点）
> - **目标对象（Target）**：通知所应用的对象

**核心学习材料 — `MyAspect5` 的 12 行被注释掉的切入点表达式**。这是讲师的演示材料，从精确到通配逐步演进：

```java
// 来源: springboot-aop-quickstart/.../aop/MyAspect5.java
//@Aspect  // ← 故意注释掉，讲解时激活
public class MyAspect5 {

    // ① 最精确：写全修饰符、返回值、包名、类名、方法名、参数全限定类型
    //@Before("execution(public void com.itheima.service.impl.DeptServiceImpl.delete(java.lang.Integer))")

    // ② 省略修饰符
    //@Before("execution(void com.itheima.service.impl.DeptServiceImpl.delete(java.lang.Integer))")

    // ③ 省略包名.类名（⚠️ 强烈不建议省略！）
    //@Before("execution(void delete(java.lang.Integer))")

    // ④ 返回值用 * 通配
    //@Before("execution(* com.itheima.service.impl.DeptServiceImpl.delete(java.lang.Integer))")

    // ⑤ 包名用 * 通配（com.*.service... 匹配 com 下任意一段）
    //@Before("execution(* com.*.service.impl.DeptServiceImpl.delete(java.lang.Integer))")

    // ⑥ 类名用 * 通配（DeptServiceImpl 变成 *）
    //@Before("execution(* com.itheima.service.impl.*.delete(java.lang.Integer))")

    // ⑦ 参数类型用 *（匹配任意一个参数）
    //@Before("execution(* com.itheima.service.impl.*.*(*))")

    // ⑧ 方法名用前缀通配（del* 匹配 delete, deleteDept 等）
    //@Before("execution(* com.itheima.service.impl.*.del*(*))")

    // ⑨ 用 .. 表示任意包深度（com 下任意子包直到 service.impl）
    //@Before("execution(* com..service.impl.DeptServiceImpl.*(..))")

    // ⑩ 【最终日常写法】匹配 service 包下所有接口的所有方法
    //@Before("execution(* com.itheima.service.*.*(..))")

    // ⑪ 匹配多个方法：|| 连接
    //@Before("execution(* com.itheima.service.impl.DeptServiceImpl.list(..)) ||" +
    //        "execution(* com.itheima.service.impl.DeptServiceImpl.delete(..))")

    // ⑫ 注解匹配：拦截所有带 @LogOperation 的方法 ← 操作日志实际用这种
    @Before("@annotation(com.itheima.anno.LogOperation)")
    public void before() {
        log.info("MyAspect5 -> before ...");
    }
}
```

**execution 表达式的结构**：

```
execution( 修饰符?  返回值类型  包名.类名?  方法名(参数类型列表) )

通配符：
*   = 匹配任意一个元素（返回值 / 类名 / 方法名 / 单个参数）
..  = 匹配任意深度（包路径中用）或任意参数（参数列表中用）

示例对照：
execution(* com.itheima.service.*.*(..))
         ↑              ↑           ↑  ↑
         任意返回值       包路径      类 方法 (..)=任意参数

execution(* com..service.impl.DeptServiceImpl.*(..))
            ↑↑                                 匹配 com 下任意子包
```

**常见错误**：省略包名和类名；`..` 和 `*` 搞混；表达式太宽拦截到 Spring 内部方法。

---

### 3. 五种通知类型 — 从 `MyAspect1` 看全貌

**`MyAspect1` 一个类展示全部五种通知**——这是最直观的对比学习材料：

```java
// 来源: springboot-aop-quickstart/.../aop/MyAspect1.java
@Slf4j
//@Aspect // ← 故意注释掉！
@Component
public class MyAspect1 {

    @Pointcut("execution(* com.itheima.service.impl.*.*(..))")
    private void pt() {}

    // 前置通知 — 目标方法运行之前运行
    @Before("pt()")
    public void before() { log.info("before ...."); }

    // 环绕通知 — 目标方法运行之前、后运行（最强大）
    @Around("pt()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        log.info("around ... before ....");
        Object result = pjp.proceed();    // ← 必须调用！否则原方法不执行
        log.info("around ... after ....");
        return result;                    // ← 必须返回！否则调用方拿到 null
    }

    // 后置通知 — 目标方法运行之后运行，无论是否出现异常都会执行
    @After("pt()")
    public void after() { log.info("after ...."); }

    // 返回后通知 — 目标方法运行之后运行，如果出现异常不会运行
    @AfterReturning("pt()")
    public void afterReturning() { log.info("afterReturning ...."); }

    // 异常后通知 — 目标方法运行之后运行，只有出现异常才会运行
    @AfterThrowing("pt()")
    public void afterThrowing() { log.info("afterThrowing ...."); }
}
```

**五种通知对比记忆**：

| 注解 | 执行时机 | 异常是否影响 |
|------|---------|:---:|
| `@Before` | 目标方法前 | 不影响 |
| `@Around` | 包围（前 + 后），由你控制 | 由你决定 |
| `@After` | 目标方法后 | **不影响**（异常也执行） |
| `@AfterReturning` | 目标方法正常返回后 | **影响**（异常不执行） |
| `@AfterThrowing` | 目标方法抛出异常后 | **影响**（正常不执行） |

**`@Around` 的两个必须**：① 必须调用 `joinPoint.proceed()`；② 必须 `return` 返回值。

---

### 4. 多个切面的执行顺序 — 从 `MyAspect2/3/4` 看 `@Order`

三个几乎一样的类，区别只在 `@Order` 的值：

```java
// MyAspect4.java → @Order(3)  ← 最小
// MyAspect3.java → @Order(5)
// MyAspect2.java → @Order(8)  ← 最大
```

**实际运行输出**：

```
MyAspect4 -> before ...    ← Order(3) 最小，before 最先执行
MyAspect3 -> before ...
MyAspect2 -> before ...    ← Order(8) 最大，before 最后执行
--- 目标方法执行 ---
MyAspect2 -> after ...     ← after 方向反过来！
MyAspect3 -> after ...
MyAspect4 -> after ...
```

**规则**：`@Order(n)` 中 `n` 越小越先执行。前置通知从小到大执行，后置通知从大到小执行——栈式调用（最外层最后返回）。

---

### 5. JoinPoint 运行时信息 — 从 `MyAspect6` 看能拿到什么

```java
// 来源: springboot-aop-quickstart/.../aop/MyAspect6.java
@Slf4j
@Aspect
@Component
public class MyAspect6 {

    @Before("execution(* com.itheima.service.*.*(..))")
    public void before(JoinPoint joinPoint) {
        log.info("before ....");

        // 1. 获取目标对象 — 被代理的那个 Bean 实例
        Object target = joinPoint.getTarget();
        log.info("获取目标对象: {}", target);

        // 2. 获取目标类全限定名 — 例如 com.itheima.service.impl.DeptServiceImpl
        String className = joinPoint.getTarget().getClass().getName();
        log.info("获取目标类: {}", className);

        // 3. 获取目标方法名 — 例如 list / delete
        String methodName = joinPoint.getSignature().getName();
        log.info("获取目标方法: {}", methodName);

        // 4. 获取目标方法的实际参数数组
        Object[] args = joinPoint.getArgs();
        log.info("获取目标方法参数: {}", Arrays.toString(args));
    }

    @Around("execution(* com.itheima.service.*.*(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        log.info("around ... before ....");
        Object result = pjp.proceed();
        log.info("around ... after ....");
        return result;
    }
}
```

**JoinPoint 的 4 个核心 API**：`getTarget()`、`getTarget().getClass().getName()`、`getSignature().getName()`、`getArgs()`。这些是操作日志切面提取方法信息的基础。

---

### 6. 操作日志 — 从 `OperationLogAspect` 看完整生产级实现

你的素材中 tlias-web-management 项目有一个**打通注解→切面→数据库**的完整实现。

#### 自定义注解

```java
// 来源: tlias-web-management/.../anno/Log.java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Log {
}
```

注解名叫 `@Log`，极其简洁——通过方法签名和参数就能区分操作，不需要额外的 value 字段。

#### 操作日志实体

```java
// 来源: tlias-web-management/.../pojo/OperateLog.java
@Data
public class OperateLog {
    private Integer id;                // 自增主键
    private Integer operateEmpId;      // 操作人ID
    private LocalDateTime operateTime; // 操作时间
    private String className;          // 操作类名（全限定名）
    private String methodName;         // 操作方法名
    private String methodParams;       // 操作方法参数（Arrays.toString）
    private String returnValue;        // 操作方法返回值
    private Long costTime;             // 操作耗时(ms)
}
```

#### Mapper — MyBatis 注解式插入

```java
// 来源: tlias-web-management/.../mapper/OperateLogMapper.java
@Mapper
public interface OperateLogMapper {
    @Insert("insert into operate_log (operate_emp_id, operate_time, class_name, " +
            "method_name, method_params, return_value, cost_time) " +
            "values (#{operateEmpId}, #{operateTime}, #{className}, #{methodName}, " +
            "#{methodParams}, #{returnValue}, #{costTime});")
    void insert(OperateLog log);
}
```

#### ThreadLocal 获取当前用户

```java
// 来源: tlias-web-management/.../utils/CurrentHolder.java
public class CurrentHolder {
    // ThreadLocal：每个线程独立存储，天然线程安全
    private static final ThreadLocal<Integer> CURRENT_LOCAL = new ThreadLocal<>();

    public static void setCurrentId(Integer employeeId) {
        CURRENT_LOCAL.set(employeeId);       // 登录拦截器校验通过后调用
    }

    public static Integer getCurrentId() {
        return CURRENT_LOCAL.get();           // 切面中调用，取出当前操作人
    }

    public static void remove() {
        CURRENT_LOCAL.remove();               // 请求结束必须清理，防内存泄漏
    }
}
```

**调用链路**：`TokenInterceptor` 解析 JWT → `CurrentHolder.setCurrentId(empId)` → `OperationLogAspect` 调用 `CurrentHolder.getCurrentId()` → 拿到操作人。

#### 切面实现

```java
// 来源: tlias-web-management/.../aop/OperationLogAspect.java
@Slf4j
@Aspect
@Component
public class OperationLogAspect {

    @Autowired
    private OperateLogMapper operateLogMapper;        // 注入 Mapper，日志写入数据库

    @Around("@annotation(com.itheima.anno.Log)")      // 匹配所有带 @Log 的方法
    public Object logOperation(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();

        // 1. 执行目标方法
        Object result = joinPoint.proceed();

        // 2. 计算耗时
        long costTime = System.currentTimeMillis() - startTime;

        // 3. 从 JoinPoint 提取一切运行时信息，构建日志实体
        OperateLog olog = new OperateLog();
        olog.setOperateEmpId(getCurrentUserId());                       // ThreadLocal 拿操作人
        olog.setOperateTime(LocalDateTime.now());
        olog.setClassName(joinPoint.getTarget().getClass().getName());  // 全限定类名
        olog.setMethodName(joinPoint.getSignature().getName());         // 方法名
        olog.setMethodParams(Arrays.toString(joinPoint.getArgs()));     // 参数
        olog.setReturnValue(result != null ? result.toString() : "void");
        olog.setCostTime(costTime);

        // 4. 持久化到数据库
        log.info("记录操作日志: {}", olog);
        operateLogMapper.insert(olog);

        return result;
    }

    private Integer getCurrentUserId() {
        return CurrentHolder.getCurrentId();
    }
}
```

**完整数据流**：

```
请求进入 → TokenInterceptor 解析 JWT → CurrentHolder.setCurrentId(empId)
    → DeptController.delete() 执行（带 @Log 注解）
        → OperationLogAspect.logOperation() 触发
            → joinPoint.proceed() → 目标方法执行完成
            → 从 joinPoint 提取方法信息
            → 从 CurrentHolder 提取用户信息
            → 计算耗时
            → 组装 OperateLog → operateLogMapper.insert() → 写入 operate_log 表
            → return result
```

**`@Aspect` 被注释的教学设计**：你的 `springboot-aop-quickstart` 中所有切面类的 `@Aspect` 都被注释掉了。这不是遗漏，而是精妙的教学设计——讲师讲到哪个概念就现场取消注释激活对应的 Aspect，学生立刻看到效果：

| 文件 | 教学用途 |
|------|---------|
| `RecordTimeAspect` | 入门：AOP 能干什么 |
| `MyAspect1` | 五种通知类型 |
| `MyAspect2/3/4` | `@Order` 执行顺序 |
| `MyAspect5` | 切入点表达式 12 种写法 |
| `MyAspect6` | JoinPoint API |

**一个切面必须满足**：`@Aspect` + `@Component` 两者缺一不可。只加 `@Aspect` 不加 `@Component`，Spring 不会管理它，AOP 不生效——这正是你代码中故意注释掉 `@Aspect` 想让学生验证的。

## 五、课堂演示

- 引入 spring-boot-starter-aop
- 编写 TimeAspect 统计业务层耗时
- 用 @LogOperation 标记增删改方法
- 记录请求人、方法名、参数、结果和耗时

## 六、课堂练习

- 实现一个操作日志切面：标注 @LogOperation 的方法执行后记录操作人、方法、参数、耗时和结果。
- 提交注解、切面类和日志示例。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 切入点范围过大导致无关方法被拦截
- 环绕通知忘记 proceed
- 日志记录敏感参数

## 九、AI 助教提示词

- 学生：我正在学习《AOP 与操作日志》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《AOP 与操作日志》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《AOP 与操作日志》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\13. 后端Web进阶(AOP)\PPT\13. 后端Web进阶(AOP).pptx（34 页）
- Slide 1: Web 后端开发 AOP
- Slide 2: AOP ： A spect O riented P rogramming （ 面向切面编程、面向方面编程 ），可简单理解为就是面向特定方法编程。 场景：案例中部分业务方法运行较慢，定位执行耗时较长的方法，此时需要统计每一个业务方法的执行耗时。 什么是 AOP public List < Dept > list (){ List < Dept > deptLi
- Slide 3: AOP ： A spect O riented P rogramming （ 面向切面编程、面向方面编程 ），可简单理解为就是面向特定方法编程。 场景：案例中部分业务方法运行较慢，定位执行耗时较长的接口，此时需要统计每一个业务方法的执行耗时。 优势： 什么是 AOP 减少重复代码 代码无侵入 提高开发效率 维护方便 AOP 是一种思想，而在 Spring 框
- Slide 4: AOP 基础 AOP 进阶 AOP 案例
- Slide 5: AOP 基础 AOP 快速入门 AOP 核心概念 01
- Slide 6: AOP 快速入门 需求：统计所有业务层方法的执行耗时。 public List < Dept > list (){ long beginTime = System.currentTimeMillis(); List < Dept > deptList = deptMapper .list(); long endTime = System . currentT
- Slide 7: SpringAOP 快速入门：统计所有业务层方法的执行耗时 导入依赖：在 pom.xml 中引入 AOP 的依赖 编写 AOP 程序：针对于特定的方法根据业务需要进行编程 < dependency > < groupId >org.springframework.boot</ groupId > < artifactId >spring-boot-start
- Slide 8: SpringAOP 程序的开发步骤 ? 引入 AOP 的依赖 编写 AOP 的程序 ( 公共的逻辑代码 ) SpringAOP 的应用场景 ? 记录系统的操作日志 事务管理 权限控制 ...
- Slide 9: AOP 基础 AOP 快速入门 AOP 核心概念 01
- Slide 10: AOP 核心概念 连接点： JoinPoint ，可以被 AOP 控制的方法（暗含方法执行时的相关信息） 通知： Advice ，指那些重复的逻辑，也就是共性功能（最终体现为一个方法） 切入点： PointCut ，匹配连接点的条件，通知仅会在切入点方法执行时被应用 切面： Aspect ，描述通知与切入点的对应关系（通知 + 切入点） 目标对象： Targ
- Slide 11: AOP 执行流程 public class DeptService Proxy implements DeptService { @Override public List<Dept> list () { long begin = System.currentTimeMillis(); List < Dept > deptList = 目标对象 .list(
- Slide 12: AOP 核心概念 连接点（ JoinPoint ） 切入点（ PointCut ） 通知（ Advice ） 切面（ Aspect ） 目标对象（ Target ）
- Slide 13: AOP 基础 AOP 进阶 AOP 案例
- Slide 14: AOP 进阶 通知类型 通知顺序 切入点表达式 连接点 02

## 十一、配套代码索引

- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\anno\LogOperation.java`
  - `public @interface LogOperation {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect1.java`
  - `//@Aspect`
  - `public class MyAspect1 {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect2.java`
  - `//@Aspect`
  - `public class MyAspect2 {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect3.java`
  - `//@Aspect`
  - `public class MyAspect3 {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect4.java`
  - `//@Aspect`
  - `public class MyAspect4 {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect5.java`
  - `//@Aspect`
  - `public class MyAspect5 {`
  - `//匹配list 与 delete 方法`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\MyAspect6.java`
  - `@Aspect`
  - `public class MyAspect6 {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\aop\RecordTimeAspect.java`
  - `//@Aspect //标识当前是一个AOP类`
  - `public class RecordTimeAspect {`
- `ppt\13. 后端Web进阶(AOP)\代码\springboot-aop-quickstart\src\main\java\com\itheima\controller\DeptController.java`
  - `@RestController`
  - `public class DeptController {`
