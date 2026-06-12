# 阶段二：SSM 后端基础功能

> 对应项目：`项目2-SSM后端基础功能/springproduct`
> 包名：`org.nong`
> 技术栈：Spring 5.3 + SpringMVC + MyBatis 3.5 + Druid + MySQL

## 一、项目概览

本阶段用传统 SSM（Spring + SpringMVC + MyBatis）搭建农博后台管理系统的全部基础功能，共 **13 个业务模块** + 1 个认证模块。

### 目录结构

```
springproduct/
├── pom.xml                          # WAR 打包，Spring 5.3.39 + MyBatis 3.5.10
└── src/main/
    ├── java/org/nong/
    │   ├── common/                  # 公共类
    │   │   ├── BaseEntity.java      # 实体基类（createBy/createTime/updateBy...）
    │   │   ├── PageQuery.java       # 分页参数（pageNum/pageSize/getOffset）
    │   │   └── Result.java          # 统一响应（code:200/500, msg, data, rows, total）
    │   ├── config/
    │   │   └── FileUploadConfig.java # 文件上传配置（WebMvcConfigurer）
    │   ├── controller/              # 13 个业务 Controller + Auth + FileUpload + Statistics + System
    │   │   ├── AuthController.java
    │   │   ├── NbAdvertisementController.java
    │   │   ├── NbAllowancePolicyController.java
    │   │   ├── NbCreditLoanController.java
    │   │   ├── NbExpertController.java
    │   │   ├── NbFarmMarketController.java
    │   │   ├── NbFarmProduceController.java
    │   │   ├── NbGraphicCourseController.java
    │   │   ├── NbServiceController.java
    │   │   ├── NbVideoCourseController.java
    │   │   ├── StatisticsController.java
    │   │   ├── SystemManagementController.java
    │   │   └── FileUploadController.java
    │   ├── entity/                  # 13 个实体类 + SysUser/SysRole/SysConfig
    │   ├── mapper/                  # Mapper 接口（不加 @Mapper，靠 XML 扫描）
    │   ├── service/                 # IXxxService 接口（I 前缀命名）
    │   ├── service/impl/            # XxxServiceImpl 实现类
    │   └── filter/
    │       └── CorsFilter.java      # CORS 跨域过滤器（javax.servlet.Filter）
    ├── resources/
    │   ├── applicationContext.xml   # Spring 核心配置（数据源/事务/Mapper 扫描）
    │   ├── spring-mvc.xml           # SpringMVC 配置（JSON 转换/文件上传/CORS）
    │   ├── jdbc.properties          # 数据库连接 + Druid 连接池参数
    │   ├── mybatis-config.xml       # MyBatis 配置（驼峰映射等）
    │   ├── logback.xml              # 日志配置
    │   └── mapper/                  # 13 个 XML 映射文件
    └── webapp/WEB-INF/
        └── web.xml                  # Servlet 配置（ContextLoaderListener/DispatcherServlet/Filter）
```

### 13 个业务模块

| 模块 | Controller | 说明 |
|------|-----------|------|
| 农产品管理 | `NbFarmProduceController` | CRUD + 推荐/推送 + 批量删除 + 导出 |
| 广告管理 | `NbAdvertisementController` | CRUD + 发布/取消 + 批量删除 |
| 农市管理 | `NbFarmMarketController` | 农贸市场 CRUD |
| 专家管理 | `NbExpertController` | 农业专家 CRUD |
| 图文课程 | `NbGraphicCourseController` | 知识课程 CRUD |
| 视频课程 | `NbVideoCourseController` | 视频课程 CRUD |
| 补贴政策 | `NbAllowancePolicyController` | 惠农政策 CRUD |
| 信贷管理 | `NbCreditLoanController` | 农业贷款 CRUD |
| 服务预约 | `NbServiceController` | 农技服务 CRUD |
| 认证登录 | `AuthController` | 用户名密码登录/Token 返回 |
| 文件上传 | `FileUploadController` | 图片/文件上传 |
| 数据统计 | `StatisticsController` | 各模块数据统计 |
| 系统管理 | `SystemManagementController` | 角色/配置管理 |

---

## 二、SSM 三大配置文件

### web.xml — Servlet 入口

```xml
<!-- 来源: 项目2/src/main/webapp/WEB-INF/web.xml -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="4.0">

    <!-- Spring 监听器 → 加载 applicationContext.xml（Service/Mapper/事务） -->
    <context-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>classpath:applicationContext.xml</param-value>
    </context-param>
    <listener>
        <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
    </listener>

    <!-- CORS 跨域过滤器 -->
    <filter>
        <filter-name>corsFilter</filter-name>
        <filter-class>org.nong.filter.CorsFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>corsFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

    <!-- SpringMVC 前端控制器 → 加载 spring-mvc.xml（Controller/JSON/文件上传） -->
    <servlet>
        <servlet-name>dispatcherServlet</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>classpath:spring-mvc.xml</param-value>
        </init-param>
        <multipart-config>
            <max-file-size>104857600</max-file-size>    <!-- 100MB -->
        </multipart-config>
    </servlet>
    <servlet-mapping>
        <servlet-name>dispatcherServlet</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>

</web-app>
```

**父子容器关系**：
- `ContextLoaderListener`（父容器）：管理 Service、Mapper、事务等
- `DispatcherServlet`（子容器）：管理 Controller、视图解析、文件上传
- 子容器可以访问父容器的 Bean（所以 Controller 可以 `@Autowired` Service）

### applicationContext.xml — Spring 核心配置

```xml
<!-- 来源: 项目2/src/main/resources/applicationContext.xml -->
<beans>

    <!-- 1. 注解扫描 — 排除 Controller（Controller 由 spring-mvc.xml 扫描） -->
    <context:component-scan base-package="org.nong">
        <context:exclude-filter type="annotation"
            expression="org.springframework.stereotype.Controller"/>
    </context:component-scan>

    <!-- 2. 加载 jdbc.properties -->
    <context:property-placeholder location="classpath:jdbc.properties"/>

    <!-- 3. Druid 数据源 -->
    <bean id="dataSource" class="com.alibaba.druid.pool.DruidDataSource" destroy-method="close">
        <property name="driverClassName" value="${jdbc.driver}"/>
        <property name="url" value="${jdbc.url}"/>
        <property name="username" value="${jdbc.username}"/>
        <property name="password" value="${jdbc.password}"/>
    </bean>

    <!-- 4. SqlSessionFactory — 指定 mybatis-config.xml 和 mapper/*.xml -->
    <bean id="sqlSessionFactory" class="org.mybatis.spring.SqlSessionFactoryBean">
        <property name="dataSource" ref="dataSource"/>
        <property name="configLocation" value="classpath:mybatis-config.xml"/>
        <property name="mapperLocations" value="classpath:mapper/*.xml"/>
    </bean>

    <!-- 5. Mapper 扫描 — 自动为 org.nong.mapper 下的接口创建代理 -->
    <bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
        <property name="basePackage" value="org.nong.mapper"/>
    </bean>

    <!-- 6. 事务管理器 + 注解驱动 -->
    <bean id="transactionManager"
          class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
        <property name="dataSource" ref="dataSource"/>
    </bean>
    <tx:annotation-driven transaction-manager="transactionManager"/>

    <!-- 7. AOP 事务增强 — 方法名匹配规则 -->
    <tx:advice id="txAdvice">
        <tx:attributes>
            <tx:method name="add*" propagation="REQUIRED"/>
            <tx:method name="insert*" propagation="REQUIRED"/>
            <tx:method name="update*" propagation="REQUIRED"/>
            <tx:method name="delete*" propagation="REQUIRED"/>
            <tx:method name="select*" propagation="SUPPORTS" read-only="true"/>
            <tx:method name="list*" propagation="SUPPORTS" read-only="true"/>
        </tx:attributes>
    </tx:advice>
    <aop:config>
        <aop:pointcut id="txPointcut" expression="execution(* org.nong.service..*.*(..))"/>
        <aop:advisor advice-ref="txAdvice" pointcut-ref="txPointcut"/>
    </aop:config>

</beans>
```

**事务策略**：以 `add/insert/save/update/delete` 开头的方法自动开启事务（REQUIRED）；以 `select/list/get/find/query` 开头的方法只读（SUPPORTS + read-only）。

### spring-mvc.xml — SpringMVC 配置

```xml
<!-- 来源: 项目2/src/main/resources/spring-mvc.xml -->
<beans>
    <!-- 只扫描 Controller 和 config 包 -->
    <context:component-scan base-package="org.nong.controller,org.nong.config"/>

    <!-- JSON 转换器 — 响应自动序列化为 JSON -->
    <mvc:annotation-driven>
        <mvc:message-converters>
            <bean class="org.springframework.http.converter.json.MappingJackson2HttpMessageConverter">
                <property name="supportedMediaTypes">
                    <list>
                        <value>application/json;charset=UTF-8</value>
                    </list>
                </property>
            </bean>
        </mvc:message-converters>
    </mvc:annotation-driven>

    <!-- 文件上传解析器 -->
    <bean id="multipartResolver"
          class="org.springframework.web.multipart.support.StandardServletMultipartResolver"/>

    <!-- CORS 全局跨域 -->
    <mvc:cors>
        <mvc:mapping path="/**" allowed-origin-patterns="*"
                     allowed-methods="GET,POST,PUT,DELETE,OPTIONS"
                     allowed-headers="*" allow-credentials="true"/>
    </mvc:cors>
</beans>
```

---

## 三、核心公共类

### Result<T> — 统一响应

```java
// 来源: 项目2/.../common/Result.java
@Data
public class Result<T> implements Serializable {
    private Integer code;    // 200=成功, 500=失败
    private String msg;
    private T data;          // 单个对象
    private Long total;      // 分页总记录数
    private T rows;          // 分页数据列表

    // 成功
    public static <T> Result<T> success() { return new Result<>(200, "操作成功"); }
    public static <T> Result<T> success(String msg) { return new Result<>(200, msg); }
    public static <T> Result<T> success(T data) {
        Result<T> r = new Result<>(200, "操作成功"); r.setData(data); return r;
    }
    public static <T> Result<T> success(T rows, Long total) {
        Result<T> r = new Result<>(200, "查询成功"); r.setRows(rows); r.setTotal(total); return r;
    }

    // 失败
    public static <T> Result<T> error(String msg) { return new Result<>(500, msg); }
    public static <T> Result<T> error(Integer code, String msg) { return new Result<>(code, msg); }

    // 将 rows+total 转换为嵌套的分页 data 结构
    public void buildPageData() {
        if (this.rows != null) {
            PageData<T> pd = new PageData<>(); pd.setRecords(this.rows); pd.setTotal(this.total);
            this.data = (T) pd;
        }
    }
}
```

### PageQuery — 分页参数

```java
// 来源: 项目2/.../common/PageQuery.java
@Data
public class PageQuery {
    private Integer pageNum = 1;
    private Integer pageSize = 10;
    public Integer getOffset() { return (pageNum - 1) * pageSize; }   // LIMIT 起始行
}
```

### BaseEntity — 实体基类

```java
// 来源: 项目2/.../common/BaseEntity.java
@Data
public class BaseEntity implements Serializable {
    private String searchValue;
    private String createBy;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;
    private String updateBy;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
    private String remark;
    private Map<String, Object> params;   // 用于存放额外查询参数
}
```

---

## 四、标准 CRUD 走读 — 以"农产品管理"为例

### Entity

```java
// 来源: 项目2/.../entity/NbFarmProduce.java
@Data
@EqualsAndHashCode(callSuper = true)
public class NbFarmProduce extends BaseEntity {
    private String id;              // UUID 主键（String 类型，非自增）
    private String title;           // 标题
    private String resume;          // 摘要
    private String description;     // 描述
    private String image;           // 图片
    private String catgory;         // 分类
    private String produceType;     // 产品类型
    private BigDecimal price;       // 价格
    private Integer browseNum;      // 浏览数
    private Integer pushStatus;     // 推送状态（0未推送 1已推送）
    private Date pushTime;          // 推送时间
    private Integer recommend;      // 推荐状态（0不推荐 1推荐）
    private String providerName;    // 供应商
    private String accountId;       // 账户ID
    private String createdTime;     // 创建时间（字符串格式）
    private String updatedTime;     // 更新时间（字符串格式）
}
```

### Mapper 接口

```java
// 来源: 项目2/.../mapper/NbFarmProduceMapper.java
public interface NbFarmProduceMapper {
    List<NbFarmProduce> selectList(Map<String, Object> params);
    Long selectCount(Map<String, Object> params);
    NbFarmProduce selectById(@Param("id") String id);
    int insert(NbFarmProduce produce);
    int update(NbFarmProduce produce);
    int deleteById(@Param("id") String id);
    int deleteBatch(@Param("ids") String[] ids);
}
```

**关键点**：
- 接口**不加** `@Mapper` 注解 — 由 `applicationContext.xml` 中的 `MapperScannerConfigurer` 统一扫描
- 使用 `Map<String, Object> params` 传参而非多个独立参数 — 便于 XML 动态 SQL
- `@Param` 注解标注单个参数名

### Mapper XML

```xml
<!-- 来源: 项目2/src/main/resources/mapper/NbFarmProduceMapper.xml -->
<mapper namespace="org.nong.mapper.NbFarmProduceMapper">

    <resultMap id="BaseResultMap" type="org.nong.entity.NbFarmProduce">
        <id property="id" column="id"/>
        <result property="produceType" column="produce_type"/>
        <result property="browseNum" column="browse_num"/>
        <result property="pushStatus" column="push_status"/>
        <result property="pushTime" column="push_time"/>
        <result property="providerName" column="provider_name"/>
        <result property="accountId" column="account_id"/>
        <result property="createdTime" column="created_time"/>
        <result property="updatedTime" column="updated_time"/>
        <!-- ... 其他字段省略 -->
    </resultMap>

    <!-- 条件分页查询 -->
    <select id="selectList" resultMap="BaseResultMap">
        SELECT * FROM nb_farm_produce
        <where>
            <if test="title != null and title != ''">
                AND title LIKE CONCAT('%', #{title}, '%')
            </if>
            <if test="catgory != null and catgory != ''">
                AND catgory = #{catgory}
            </if>
            <if test="pushStatus != null">
                AND push_status = #{pushStatus}
            </if>
            <if test="recommend != null">
                AND recommend = #{recommend}
            </if>
        </where>
        ORDER BY created_time DESC
        <if test="offset != null and pageSize != null">
            LIMIT #{offset}, #{pageSize}
        </if>
    </select>

    <!-- 计数查询（分页用） -->
    <select id="selectCount" resultType="long">
        SELECT COUNT(*) FROM nb_farm_produce
        <where> <!-- 与 selectList 条件一致 --> </where>
    </select>

    <!-- 新增 -->
    <insert id="insert">
        INSERT INTO nb_farm_produce (id, title, catgory, ...)
        VALUES (#{id}, #{title}, #{catgory}, ...)
    </insert>

    <!-- 更新 — 动态 SET：只更新非空字段 -->
    <update id="update">
        UPDATE nb_farm_produce
        <set>
            <if test="title != null">title = #{title},</if>
            <if test="catgory != null">catgory = #{catgory},</if>
            <if test="pushStatus != null">push_status = #{pushStatus},</if>
            <!-- ... -->
        </set>
        WHERE id = #{id}
    </update>

    <!-- 批量删除 — foreach -->
    <delete id="deleteBatch">
        DELETE FROM nb_farm_produce WHERE id IN
        <foreach collection="ids" item="id" open="(" separator="," close=")">
            #{id}
        </foreach>
    </delete>
</mapper>
```

**XML 动态 SQL 标签速查**：

| 标签 | 作用 |
|------|------|
| `<if test="...">` | 条件判断 |
| `<where>` | 包裹条件，自动去掉多余 AND/OR |
| `<set>` | UPDATE 时自动去掉末尾逗号 |
| `<foreach>` | 遍历集合（批量操作 / IN 查询） |

### Service 接口

```java
// 来源: 项目2/.../service/INbFarmProduceService.java
public interface INbFarmProduceService {
    Result<NbFarmProduce> selectList(Map<String, Object> params);   // 分页查询 → 返回封装好的 Result
    NbFarmProduce selectById(String id);                             // 查单个 → 返回实体
    int insert(NbFarmProduce produce);
    int update(NbFarmProduce produce);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}
```

**命名规范**：接口名 `IXxxService`（I 前缀），实现类 `XxxServiceImpl`。

### Service 实现

```java
// 来源: 项目2/.../service/impl/NbFarmProduceServiceImpl.java
@Service
public class NbFarmProduceServiceImpl implements INbFarmProduceService {

    @Autowired
    private NbFarmProduceMapper produceMapper;

    @Override
    public Result<NbFarmProduce> selectList(Map<String, Object> params) {
        List<NbFarmProduce> list = produceMapper.selectList(params);
        Long total = produceMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);          // 设置列表数据
        result.setTotal(total);         // 设置总记录数
        result.buildPageData();         // 转换为嵌套分页结构
        return result;
    }

    @Override
    public int insert(NbFarmProduce produce) {
        if (produce.getId() == null || produce.getId().isEmpty()) {
            produce.setId(UUID.randomUUID().toString().replace("-", ""));  // UUID 主键
        }
        return produceMapper.insert(produce);
    }

    // selectById/update/deleteById/deleteBatch 直接透传 Mapper
}
```

**关键模式**：
- **分页**：先查 `selectList` → 再查 `selectCount` → 分别设置 `rows` 和 `total` → `buildPageData()`
- **主键策略**：`String` 类型 + `UUID.randomUUID().toString().replace("-", "")`，插入前生成（不需要主键回填）
- **Service 返回 `Result`**：Controller 直接透传 Service 的结果

### Controller

```java
// 来源: 项目2/.../controller/NbFarmProduceController.java
@RestController
@RequestMapping("/api/yjnb/produce")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbFarmProduceController {

    @Autowired
    private INbFarmProduceService produceService;

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
        return produceService.selectList(params);
    }

    @GetMapping("/{id}")
    public Result<NbFarmProduce> getById(@PathVariable String id) {
        return Result.success(produceService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbFarmProduce produce) {
        produceService.insert(produce);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbFarmProduce produce) {
        produceService.update(produce);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        produceService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        produceService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/recommendFarmProduce")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);           // 私有方法封装状态更新
    }

    private Map<String, Object> buildParams(PageQuery pageQuery, ...) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        // ... 所有查询条件放入 Map
        return params;
    }
}
```

**Controller 模式总结**：

| 模式 | 说明 |
|------|------|
| `PageQuery` 自动绑定 | 前端传 `pageNum`/`pageSize`，`getOffset()` 计算 LIMIT 起始行 |
| `Map<String, Object> params` | Controller 构建查询条件 Map 传给 Service → Mapper |
| `@CrossOrigin` | 每个 Controller 都加，允许跨域 |
| `@RequestParam(required = false)` | 可选查询参数 |
| `Result.success("XXX successfully")` | 增删改返回英文操作提示 |

---

## 五、认证登录

```java
// 来源: 项目2/.../controller/AuthController.java
@RestController
@RequestMapping("/api/yjnb/system")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class AuthController {

    @Autowired
    private ISysUserService userService;

    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        if (username == null || username.trim().isEmpty())
            return Result.error("Username is required");
        if (password == null || password.trim().isEmpty())
            return Result.error("Password is required");

        SysUser user = userService.selectByUsername(username);
        if (user == null || !password.equals(user.getPassword()))
            return Result.error("Username or password is incorrect");
        if (user.getStatus() != null && user.getStatus() == 1)
            return Result.error("User account is disabled");

        user.setLoginIp("127.0.0.1");
        user.setLoginDate(LocalDateTime.now().format(
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        userService.update(user);

        Map<String, Object> data = new HashMap<>();
        data.put("token", "TOKEN_" + username + "_" + UUID.randomUUID().toString().replace("-", ""));
        data.put("username", user.getUsername());
        data.put("role", "admin".equals(username) ? "超级管理员" : "普通用户");
        return Result.success("Login successful", data);
    }
}
```

**登录流程**：参数校验 → 查数据库 → 密码比对 → 状态校验 → 更新登录记录 → 生成简单 Token → 返回。

本阶段使用**简单 Token（UUID 拼接）**而非 JWT，适合学习阶段理解"登录后如何证明身份"的核心思想。

---

## 六、CORS 跨域滤镜

```java
// 来源: 项目2/.../filter/CorsFilter.java
public class CorsFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
        HttpServletResponse response = (HttpServletResponse) res;
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", "POST, GET, PUT, OPTIONS, DELETE, PATCH");
        response.setHeader("Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept, Authorization, token");
        if ("OPTIONS".equalsIgnoreCase(((HttpServletRequest) req).getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        chain.doFilter(req, res);
    }
}
```

---

## 七、文件上传配置

```java
// 来源: 项目2/.../config/FileUploadConfig.java
@Configuration
public class FileUploadConfig implements WebMvcConfigurer {
    @Value("${file.upload.path:./uploads}")   private String uploadPath;
    @Value("${file.access.prefix:/uploads}")  private String accessPrefix;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path uploadRoot = resolveUploadRoot();
        registry.addResourceHandler(accessPrefix + "/**")
                .addResourceLocations(uploadRoot.toUri().toString());
    }
}
```

---

## 八、技术栈总结

| 层级 | 技术 | 版本 |
|------|------|------|
| 框架 | Spring + SpringMVC | 5.3.39 |
| ORM | MyBatis | 3.5.10 |
| 连接池 | Druid | 1.2.23 |
| 数据库 | MySQL | 8.0 |
| JSON | Jackson | 2.15.4 |
| 工具 | Lombok | 1.18.32 |
| 日志 | SLF4J + Logback | 2.0.13 / 1.4.14 |
| 文件上传 | Commons FileUpload | 1.5 |
| 打包 | WAR | — |
| JDK | 17 | — |
