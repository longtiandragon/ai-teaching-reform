# 第04讲：JDBC、连接池与 MyBatis 入门

> 课程来源：06. 后端Web基础(java操作数据库)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

从 JDBC 规范和 PreparedStatement 出发，引出连接池、MyBatis Mapper、XML/注解 SQL 与 SpringBoot 整合。

**本讲主线：** 让学生先感受 JDBC 的重复代码，再理解 MyBatis 为什么能把 SQL 与对象映射组织起来。

## 二、学习目标

- 理解 JDBC 是 Java 操作关系型数据库的 API 规范
- 能使用 PreparedStatement 防止 SQL 注入
- 了解连接池降低连接创建成本
- 能编写 Mapper 接口完成基础 CRUD

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

> **说明**：本讲 JDBC 和 MyBatis 注解方式部分保留 PPT 教学代码（`com.itheima` 包）；MyBatis XML 方式使用农博项目（`org.nong` 包）的实际写法。两者都需要掌握。

### 补充：MyBatis XML 映射 — 农博项目的实际写法

农博项目使用 **XML 映射**而非注解 SQL，这是企业项目的常见选择——SQL 与 Java 代码分离，复杂查询（动态条件、多表连接）更易维护。

**Mapper 接口**（不加 `@Mapper` 注解，由 XML 扫描配置管理）：

```java
// 来源: 农博项目/.../mapper/NbFarmProduceMapper.java
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

**XML 映射文件**（`src/main/resources/mapper/NbFarmProduceMapper.xml`）：

```xml
<!-- 来源: 农博项目/mapper/NbFarmProduceMapper.xml -->
<mapper namespace="org.nong.mapper.NbFarmProduceMapper">

    <!-- 结果映射：数据库下划线 → Java 驼峰 -->
    <resultMap id="BaseResultMap" type="org.nong.entity.NbFarmProduce">
        <id property="id" column="id"/>
        <result property="produceType" column="produce_type"/>
        <result property="browseNum" column="browse_num"/>
        <result property="pushStatus" column="push_status"/>
        <!-- ... -->
    </resultMap>

    <!-- 条件分页查询 — 动态 SQL -->
    <select id="selectList" resultMap="BaseResultMap">
        SELECT id, title, catgory, produce_type, price, browse_num, ...
        FROM nb_farm_produce
        <where>
            <if test="title != null and title != ''">
                AND title LIKE CONCAT('%', #{title}, '%')
            </if>
            <if test="catgory != null and catgory != ''">
                AND catgory = #{catgory}
            </if>
        </where>
        ORDER BY created_time DESC
        <if test="offset != null and pageSize != null">
            LIMIT #{offset}, #{pageSize}
        </if>
    </select>

    <!-- 计数查询（用于分页） -->
    <select id="selectCount" resultType="long">
        SELECT COUNT(*) FROM nb_farm_produce
        <where>
            <if test="title != null and title != ''">
                AND title LIKE CONCAT('%', #{title}, '%')
            </if>
        </where>
    </select>

    <!-- 新增 -->
    <insert id="insert">
        INSERT INTO nb_farm_produce (id, title, catgory, produce_type, ...
        ) VALUES (#{id}, #{title}, #{catgory}, #{produceType}, ...)
    </insert>

    <!-- 更新 — 动态 SET -->
    <update id="update">
        UPDATE nb_farm_produce
        <set>
            <if test="title != null">title = #{title},</if>
            <if test="catgory != null">catgory = #{catgory},</if>
            <if test="pushStatus != null">push_status = #{pushStatus},</if>
            ...
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

**XML 动态 SQL 核心标签**：

| 标签 | 作用 | 农博示例 |
|------|------|---------|
| `<if test="...">` | 条件判断 | `AND title LIKE CONCAT('%', #{title}, '%')` |
| `<where>` | 自动去掉多余的 AND/OR | 包裹所有条件 |
| `<set>` | 自动去掉末尾逗号 | `UPDATE ... SET` 中 |
| `<foreach>` | 遍历集合 | 批量删除 `IN (...)` |
| `<sql>` + `<include>` | 复用 SQL 片段 | `selectColumns` |

**XML 方式 vs 注解方式**：

| | XML 映射 | 注解 SQL |
|---|---|---|
| SQL 位置 | 独立 XML 文件 | Java 代码中 |
| 复杂 SQL | 适合（动态条件、多表） | 繁琐 |
| SQL 热更新 | 修改 XML 不重启 | 需重新编译 |
| 农博项目 | ✅ 全部用 XML | 不用 |
| PPT 教学项目 | 部分用 | ✅ 全用 `@Select/@Insert` |

### 1. JDBC 是什么 — 从 `JdbcTest.testUpdate` 看原始操作

PPT Slide 6 给出了 JDBC 的定义：**JDBC（Java DataBase Connectivity）**，就是使用 Java 语言操作关系型数据库的一套 API。本质是 Sun 公司定义的一套操作所有关系型数据库的**接口规范**，由各数据库厂商实现。

**JDBC 操作步骤（DML — 增删改）**：

```java
// 来源: jdbc-demo/.../JdbcTest.java — testUpdate()
@Test
public void testUpdate() throws Exception {
    // 1. 注册驱动
    Class.forName("com.mysql.cj.jdbc.Driver");

    // 2. 获取数据库连接
    String url = "jdbc:mysql://localhost:3306/web01";
    String username = "root";
    String password = "1234";
    Connection connection = DriverManager.getConnection(url, username, password);

    // 3. 获取 SQL 语句执行对象
    Statement statement = connection.createStatement();

    // 4. 执行 SQL（DML: INSERT/UPDATE/DELETE）
    int i = statement.executeUpdate("update user set age = 25 where id = 1");
    System.out.println("SQL执行完毕影响的记录数为: " + i);

    // 5. 释放资源（必须手动关闭！）
    statement.close();
    connection.close();
}
```

**五步总结**：注册驱动 → 获取连接 → 创建 Statement → 执行 SQL → 释放资源。

### 2. PreparedStatement 与 SQL 注入防护 — 从 `testSelect` 看 DQL 操作

**问题**：上面用 `Statement` 拼接 SQL 存在 SQL 注入风险。如果用户输入 `' OR '1'='1`，SQL 语义会被篡改。

**解决方案 — PreparedStatement**：

```java
// 来源: jdbc-demo/.../JdbcTest.java — testSelect()
@Test
public void testSelect() {
    Connection conn = null;
    PreparedStatement stmt = null;
    ResultSet rs = null;

    try {
        Class.forName("com.mysql.cj.jdbc.Driver");
        conn = DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/web01", "root", "1234");

        // 预编译 SQL — ? 是占位符，用 setXxx() 填充，自动转义
        String sql = "SELECT id, username, password, name, age FROM user " +
                     "WHERE username = ? AND password = ?";
        stmt = conn.prepareStatement(sql);
        stmt.setString(1, "daqiao");    // 第1个 ? 的值
        stmt.setString(2, "123456");    // 第2个 ? 的值

        rs = stmt.executeQuery();        // DQL 用 executeQuery()

        // 处理结果集 ResultSet
        while (rs.next()) {
            User user = new User(
                rs.getInt("id"),
                rs.getString("username"),
                rs.getString("password"),
                rs.getString("name"),
                rs.getInt("age")
            );
            System.out.println(user);
        }
    } catch (SQLException se) {
        se.printStackTrace();
    } finally {
        // 5. 释放资源（倒序关闭）
        try {
            if (rs != null) rs.close();
            if (stmt != null) stmt.close();
            if (conn != null) conn.close();
        } catch (SQLException se) { se.printStackTrace(); }
    }
}
```

**PreparedStatement 的两大优势（PPT Slide 12）**：
- **安全**：防止 SQL 注入。`?` 占位符传入的值会被自动转义，无法篡改 SQL 结构
- **性能更高**：同一条 SQL 模板只需编译一次（MySQL 会对预编译 SQL 做缓存），后续只需传入不同参数值

| | Statement | PreparedStatement |
|---|---|---|
| SQL 写法 | 字符串拼接 | `?` 占位符 |
| SQL 注入 | 有风险 | 安全（自动转义） |
| 预编译 | 每次重新编译 | 一次编译多次使用 |

### 3. 数据库连接池

**为什么需要连接池**：JDBC 每次操作都要 `DriverManager.getConnection()` 新建连接，操作完又要 `close()`。数据库连接是有成本的（TCP 握手、认证），高并发下频繁创建/销毁连接性能很差。

**连接池思路**：提前创建一批连接放在"池"里，用时借一个，用完还回去，不真正关闭。你的配置中使用的连接池：

```properties
# 来源: ppt/06/代码/application.properties
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource   # 使用 Druid 连接池
spring.datasource.url=jdbc:mysql://localhost:3306/web01
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.username=root
spring.datasource.password=1234
```

Druid（德鲁伊）是阿里巴巴开源的数据库连接池，内置监控功能。

### 4. MyBatis — JDBC 到 ORM 的跃迁

**JDBC 的痛点**：硬编码 SQL、手动 set/get 字段值、手动管理连接和资源释放、大量重复代码。

**MyBatis 的解决方案**：你只需要定义 Mapper 接口 + 注解或 XML 写 SQL，MyBatis 自动生成代理实现类，完成从 ResultSet 到 Java 对象的映射。

```java
// 来源: aliyun-mybatis-quickstart/.../mapper/UserMapper.java
@Mapper  // 运行时自动创建代理实现类，并存入 IOC 容器
public interface UserMapper {

    // 查询 — 注解中写 SQL，方法返回类型决定映射目标
    @Select("select id, username, password, name, age from user")
    List<User> findAll();

    // 删除 — #{id} 替换为方法参数值
    @Delete("delete from user where id = #{id}")
    Integer deleteById(Integer id);

    // 新增 — #{username} 取的是 User 对象的 username 属性
    @Insert("insert into user(username, password, name, age) " +
            "values (#{username}, #{password}, #{name}, #{age})")
    void insert(User user);

    // 更新
    @Update("update user set username = #{username}, password = #{password}, " +
            "name = #{name}, age = #{age} where id = #{id}")
    void update(User user);

    // 多参数 — 用 @Param 指定参数名
    @Select("select * from user where username = #{username} and password = #{password}")
    User findByUsernameAndPassword(@Param("username") String username,
                                    @Param("password") String password);
}
```

**MyBatis 四大核心注解**：

| 注解 | SQL 类型 | 示例 |
|------|---------|------|
| `@Select` | DQL 查询 | `@Select("select * from user")` |
| `@Insert` | DML 新增 | `@Insert("insert into user(...) values(...)")` |
| `@Update` | DML 修改 | `@Update("update user set ... where id = #{id}")` |
| `@Delete` | DML 删除 | `@Delete("delete from user where id = #{id}")` |

**`#{}` vs `${}`**：
- `#{}` — 预编译占位符，安全，自动加引号，能防止 SQL 注入。**增删改查都用它**
- `${}` — 字符串拼接，不安全，用于动态表名/列名等无法预编译的场景。**非必要不用**

**JDBC vs MyBatis 对比**：

| | JDBC | MyBatis |
|---|---|---|
| SQL 硬编码 | 写在 Java 字符串里 | 注解或 XML，分离 |
| 参数绑定 | `stmt.setString(1, val)` 手动逐个设置 | `#{propertyName}` 自动映射 |
| 结果封装 | `rs.getInt("id")` 手动逐个 get | 自动映射到 Java 对象 |
| 资源管理 | try-catch-finally 手动关闭 | 自动管理 |
| 代码量 | 大量重复 | 只有接口 + SQL |

## 五、课堂演示

- 用 JDBC 执行 update/select 并封装 User
- 把硬编码 SQL 改为 PreparedStatement
- 创建 MyBatis Mapper 并在 SpringBoot 中测试查询

## 六、课堂练习

- 将 JDBC 登录查询改造成 MyBatis Mapper，并说明 SQL 注入防护点。
- 提交 Mapper 接口、SQL 映射和测试入口。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 资源未关闭导致连接泄露
- 字符串拼接 SQL
- 字段名与对象属性映射不清晰

## 九、AI 助教提示词

- 学生：我正在学习《JDBC、连接池与 MyBatis 入门》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《JDBC、连接池与 MyBatis 入门》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《JDBC、连接池与 MyBatis 入门》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\06. 后端Web基础(java操作数据库)\PPT\Day06. 后端Web基础(java操作数据库).pptx（49 页）
- Slide 1: Web 后端开发 java 程序操作数据库
- Slide 2: java 程序操作数据库 MyBatis MyBatisPlus SpringData JPA Hibernate JDBC ： ( J ava D ata B ase C onnectivity) ，就是使用 Java 语言操作关系型数据库的一套 API 。
- Slide 3: java 程序操作数据库 MyBatis MyBatisPlus JDBC
- Slide 4: JDBC MyBatis
- Slide 5: JDBC 01
- Slide 6: JDBC ： ( J ava D ata B ase C onnectivity) ，就是使用 Java 语言操作关系型数据库的一套 API 。 JDBC- 介绍 驱动 Java 程序 JDBC Mysql 实现 Oracle 实现 SqlServer 实现 本质： sun 公司官方定义的一套操作所有关系型数据库的规范，即接口。 各个数据库厂商去实现这套接口
- Slide 7: 需求：基于 JDBC 程序，执行 update 语句 ( update user set age = 25 where id = 1 ) 步骤： 准备工作：创建一个 maven 项目，引入依赖；并准备数据库表 user 。 代码实现：编写 JDBC 程序，操作数据库 JDBC- 入门程序 < dependency > < groupId >com.mysql
- Slide 8: 什么是 JDBC ? sun 公司提供的一套操作关系型数据库的 API （规范）。 JDBC 操作数据库步骤 DML
- Slide 9: 需求：基于 JDBC 执行如下 select 语句，将查询结果封装到 User 对象中。 SQL ： select * from user where username = 'daqiao' and password = '123456' ResultSet （结果集对象）： ResultSet rs = statement.executeQuery() n
- Slide 10: JDBC 程序执行 DML 语句 ? DQL 语句 ? DML 语句： int rowsAffected = statement.executeUpdate(); DQL 语句： ResultSet rs = statement.executeQuery(); DQL 语句执行完毕结果集 ResultSet 解析 ? resultSet.next() ：光标
- Slide 11: 预编译 SQL Statement statement = connection .createStatement(); int i = statement .executeUpdate( "update user set age = 25 where id = 1" ); System . out .println( "SQL执行完毕, 影响的记录数为: 
- Slide 12: 优势一：可以防止 SQL 注入，更安全 SQL 注入：通过控制输入来修改事先定义好的 SQL 语句，以达到执行代码对服务器进行 攻击 的方法。 预编译 SQL 优势二：性能更高 delete from user where id = 1 ; delete from user where id = 2 ; delete from user where id =
- Slide 13: 如何执行预编译 SQL ？ 为什么要使用预编译 SQL ？ 安全（防止 SQL 注入） 性能更高
- Slide 16: Mybatis 入门程序 JDBC VS Mybatis 数据库连接池 增删改查操作 XML 映射配置 02

## 十一、配套代码索引

- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\main\java\com\itheima\AliyunMybatisQuickstartApplication(1).java`
  - `@SpringBootApplication`
  - `public class AliyunMybatisQuickstartApplication {`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\main\java\com\itheima\AliyunMybatisQuickstartApplication.java`
  - `@SpringBootApplication`
  - `public class AliyunMybatisQuickstartApplication {`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\main\java\com\itheima\mapper\UserMapper.java`
  - `@Mapper //应用程序在运行时, 会自动的为该接口创建一个实现类对象(代理对象), 并且会自动将该实现类对象存入IOC容器 - bean`
  - `public interface UserMapper {`
  - `@Select("select id, username, password, name, age from user")`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\main\java\com\itheima\pojo\User.java`
  - `public class User {`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\main\resources\application.properties`
  - `spring.datasource.url=jdbc:mysql://localhost:3306/web01`
  - `spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver`
  - `spring.datasource.username=root`
- `ppt\06. 后端Web基础(java操作数据库)\代码\aliyun-mybatis-quickstart\src\test\java\com\itheima\AliyunMybatisQuickstartApplicationTests.java`
  - `class AliyunMybatisQuickstartApplicationTests {`
- `ppt\06. 后端Web基础(java操作数据库)\代码\application.properties`
  - `spring.datasource.type=com.alibaba.druid.pool.DruidDataSource`
  - `spring.datasource.url=jdbc:mysql://localhost:3306/web01`
  - `spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver`
- `ppt\06. 后端Web基础(java操作数据库)\代码\application.yml`
- `ppt\06. 后端Web基础(java操作数据库)\代码\jdbc-demo\pom.xml`
  - `<dependency>`
  - `<dependency>`
  - `<dependency>`
