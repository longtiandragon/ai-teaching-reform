# 第01讲：Maven 基础与 Java 项目构建

> 课程来源：03. 后端Web基础(Maven基础)。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。

## 一、课堂定位

让学生理解 Maven 的项目结构、依赖坐标、生命周期和测试打包流程，为后续 SpringBoot 工程做准备。

**本讲主线：** Maven 不是背命令，而是用统一结构和生命周期把 Java 项目的构建、依赖、测试、打包变成可复现流程。

## 二、学习目标

- 解释 Maven 的作用：项目构建、统一结构、依赖管理
- 读懂 pom.xml 中 groupId、artifactId、version、dependency
- 能使用 compile、test、package 完成基础构建
- 能说明本地仓库、中央仓库、依赖传递的关系

## 三、建议课时与课堂流程

- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。
- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。
- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。
- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。
- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。

## 四、核心知识点

### 1. Maven 是什么、解决什么问题

PPT Slide 4-5 给出了定义：**Maven 是一款用于管理和构建 Java 项目的工具**，Apache 旗下的开源项目。

**三大核心作用（PPT Slide 5-12）**：

| 作用 | 说明 | 为什么要用它 |
|------|------|-------------|
| **依赖管理** | 通过 pom.xml 声明依赖，自动从中央仓库下载 jar | 不用手动下载/复制 jar 包 |
| **统一项目结构** | 规定了 `src/main/java`（主程序）、`src/test/java`（测试程序）等标准目录 | 不同 IDE（Eclipse/IDEA）打开项目结构一致 |
| **项目构建** | 提供标准化的生命周期：compile → test → package → deploy | 跨平台自动化构建 |

### 2. 依赖坐标与 pom.xml — 从 `maven-project01` 看真实配置

你的配套代码 `maven-project01/pom.xml`：

```xml
<!-- 来源: maven-project01/pom.xml -->
<groupId>com.itheima</groupId>            <!-- 组织/公司标识 -->
<artifactId>maven-project01</artifactId>  <!-- 项目/模块名 -->
<version>1.0-SNAPSHOT</version>           <!-- 版本号，SNAPSHOT=开发中 -->

<dependencies>
    <!-- Spring 依赖 -->
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-context</artifactId>
        <version>6.1.4</version>
        <!-- 排除不需要的传递依赖 -->
        <exclusions>
            <exclusion>
                <groupId>io.micrometer</groupId>
                <artifactId>micrometer-observation</artifactId>
            </exclusion>
        </exclusions>
    </dependency>

    <!-- JUnit 测试依赖 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.9.1</version>
        <scope>test</scope>   <!-- 只在测试时可用，不打入最终 jar -->
    </dependency>
</dependencies>
```

**坐标三要素**（PPT Slide 6）：`groupId` + `artifactId` + `version` 唯一定位一个 jar 包。就像快递地址，通过这三个信息从 Maven 仓库中找到唯一的包。

**仓库体系**：本地仓库（你电脑上的 `.m2` 目录）← 私服（公司内部）← 中央仓库（Maven 官方）。查找顺序：先本地 → 没找到则向上一层请求。

**依赖传递**：你引入 `spring-context`，它内部依赖的 `spring-core`、`spring-beans` 等也会自动下载。如果不需要某个传递依赖，用 `<exclusion>` 排除。

**`<scope>` 依赖范围**：

| scope 值 | 主程序可用 | 测试可用 | 打包进 jar | 示例 |
|-----------|:---:|:---:|:---:|------|
| `compile`（默认） | ✅ | ✅ | ✅ | spring-context |
| `test` | ❌ | ✅ | ❌ | junit-jupiter |
| `provided` | ✅ | ✅ | ❌ | servlet-api |
| `runtime` | ❌ | ✅ | ✅ | mysql-connector |

### 3. 单元测试与 JUnit — 从 `UserServiceTest` 看实战

你的 `maven-project01` 中包含了一个业务类 `UserService`（根据身份证号计算年龄和性别），以及配套的测试类：

```java
// 来源: maven-project01/.../UserService.java
public class UserService {

    // 给定身份证号, 计算出该用户的年龄
    public Integer getAge(String idCard) {
        if (idCard == null || idCard.length() != 18) {
            throw new IllegalArgumentException("无效的身份证号码");
        }
        String birthday = idCard.substring(6, 14);
        LocalDate parse = LocalDate.parse(birthday, DateTimeFormatter.ofPattern("yyyyMMdd"));
        return Period.between(parse, LocalDate.now()).getYears();
    }

    // 给定身份证号, 计算出该用户的性别
    public String getGender(String idCard) {
        if (idCard == null || idCard.length() != 18) {
            throw new IllegalArgumentException("无效的身份证号码");
        }
        return Integer.parseInt(idCard.substring(16, 17)) % 2 == 1 ? "男" : "女";
    }
}
```

```java
// 来源: maven-project01/.../UserServiceTest.java
@DisplayName("用户信息测试类")
public class UserServiceTest {

    @Test
    public void testGetAge() {
        UserService userService = new UserService();
        Integer age = userService.getAge("100000200010011011");
        System.out.println(age);
    }

    // 断言 — 不只看输出，要自动判断结果是否正确
    @Test
    public void testGenderWithAssert() {
        UserService userService = new UserService();
        String gender = userService.getGender("100000200010011011");
        Assertions.assertEquals("男", gender, "性别获取错误有问题");
    }

    // 断言抛出异常
    @Test
    public void testGenderWithAssert2() {
        UserService userService = new UserService();
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            userService.getGender(null);
        });
    }

    // 参数化测试 — 一组数据跑同一个测试方法
    @DisplayName("测试用户性别")
    @ParameterizedTest
    @ValueSource(strings = {"100000200010011011", "100000200010011031", "100000200010011051"})
    public void testGetGender2(String idCard) {
        UserService userService = new UserService();
        String gender = userService.getGender(idCard);
        Assertions.assertEquals("男", gender);
    }
}
```

**JUnit 常用注解/方法**：

| 注解/方法 | 含义 |
|-----------|------|
| `@Test` | 标记一个测试方法 |
| `@BeforeEach` | 每个 `@Test` 方法运行前执行一次 |
| `@AfterEach` | 每个 `@Test` 方法运行后执行一次 |
| `@BeforeAll` (static) | 所有测试方法运行前执行一次 |
| `@AfterAll` (static) | 所有测试方法运行后执行一次 |
| `@DisplayName` | 给测试类/方法取可读名称 |
| `@ParameterizedTest` + `@ValueSource` | 用多组数据跑同一个测试 |
| `Assertions.assertEquals(expected, actual)` | 断言：期望值与实际值相等 |
| `Assertions.assertThrows(Exception.class, () -> {...})` | 断言：代码应抛出指定异常 |

### 4. Maven 生命周期与构建命令

PPT Slide 8-9 展示了标准化的构建生命周期：

```
compile  →  test  →  package  →  deploy
(编译)      (测试)    (打包)      (发布)
```

**常用命令**：

| 命令 | 作用 | 会连带执行 |
|------|------|-----------|
| `mvn compile` | 编译 `src/main/java` 下的源码 | — |
| `mvn test` | 编译 + 运行 `src/test/java` 下的测试 | compile |
| `mvn package` | 编译 + 测试 + 打包成 jar | compile + test |
| `mvn clean` | 删除 `target` 目录 | — |

执行后面的阶段会自动触发前面的阶段。例如 `mvn package` 会自动先执行 compile 和 test。

**构建产物**：`mvn package` 后在 `target/` 目录下生成 `.jar` 文件。你的 `maven-project01` 的 target 目录中就包含了 `maven-project01-1.0-SNAPSHOT.jar`。

## 五、课堂演示

- 展示普通 Java 项目到 Maven 项目的目录变化
- 修改 pom.xml 增加 commons-io 或 JUnit 依赖
- 运行测试并打包 jar，观察 target 目录变化

## 六、课堂练习

- 补全一个 Maven 项目的 pom.xml，添加 JUnit 依赖并编写一个 Service 单元测试。
- 学生需提交 pom.xml、测试类和 mvn test/package 的结果说明。

## 七、验收标准

- 能画出本讲相关调用链或数据流。
- 能说明关键注解、SQL、配置或 Maven 坐标的作用。
- 能提交可读的代码片段，并解释失败场景。
- AI 助教回答应能引用本讲资料或对应代码片段。

## 八、易错点与教师干预

- 把 Maven 当成 IDE 插件，只会点按钮不会解释生命周期
- 依赖版本写错或 scope 理解错误
- 源码目录、测试目录放错导致编译失败

## 九、AI 助教提示词

- 学生：我正在学习《Maven 基础与 Java 项目构建》，请用当前章节资料解释核心流程，并给出一个常见错误。
- 学生：请根据《Maven 基础与 Java 项目构建》生成一道课堂练习，要求包含代码骨架和检查清单。
- 教师：请汇总学生在《Maven 基础与 Java 项目构建》中最容易混淆的 3 个概念，并给出补讲建议。

## 十、PPT 来源摘录

- ppt\03. 后端Web基础(Maven基础)\PPT\day03-Maven基础.pptx（70 页）
- Slide 1: Web 开发 (AI)
- Slide 2: Web 开发 Web 前端基础 Web 后端基础 Web 后端实战 Web 前端实战 Web 项目部署 HTML CSS JavaScript Vue3 Ajax/Axios Maven Web 基础知识 MySQL JDBC Mybatis Tlias 案例 Tlias 案例 Linux Docker
- Slide 3: Web 后端基础 Maven
- Slide 4: 什么是 Maven 是一款用于管理和构建 Java 项目的工具，是 apache 旗下的一个开源项目。 Apache 软件基金会，成立于 1999 年 7 月，是目前世界上最大的最受欢迎的开源软件基金会，也是一个专门为支持开源项目而生的非盈利性组织。 开源项目： https://www.apache.org/index.html#projects-list
- Slide 5: Maven 的作用 项目构建 标准化的跨平台（ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 统一项目结构 提供标准、统一的项目结构 依赖管理 方便快捷的管理项目依赖的资源（ jar 包）
- Slide 6: Maven 的作用 依赖管理 方便快捷的管理项目依赖的资源（ jar 包） < dependency > < groupId >commons-io</ groupId > < artifactId >commons-io</ artifactId > < version >2.11.0</ version > </ dependency >
- Slide 7: Maven 的作用 项目构建 标准化的跨平台 （ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 统一项目结构 提供标准、统一的项目结构 依赖管理 方便快捷的管理项目依赖的资源 （ jar 包）
- Slide 8: Maven 的作用 项目构建 标准化的跨平台（ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 编译 测试 打包 发布
- Slide 9: Maven 的作用 项目构建 标准化的跨平台（ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 编译 (compile) 测试 (test) 打包 (package) 发布 (deploy)
- Slide 10: Maven 的作用 项目构建 标准化的跨平台（ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 统一项目结构 提供标准、统一的项目结构 依赖管理 方便快捷的管理项目依赖的资源（ jar 包）
- Slide 11: Maven 的作用 统一项目结构 提供标准、统一的项目结构 Eclipse MyEclipse IntelliJ IDEA 主程序 测试程序
- Slide 12: Maven 的作用 项目构建 标准化的跨平台（ Linux 、 Windows 、 MacOS ）的自动化项目构建方式 统一项目结构 提供标准、统一的项目结构 依赖管理 方便快捷的管理项目依赖的资源（ jar 包）
- Slide 14: Maven 核心 Maven 进阶
- Slide 15: Maven 核心 Maven 进阶 Maven 概述 IDEA 集成 Maven 依赖管理 单元测试 分模块设计 继承 聚合 私服

## 十一、配套代码索引

- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\pom.xml`
  - `<dependency>`
  - `<dependency>`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\src\main\java\com\itheima\HelloWorld.java`
  - `public class HelloWorld {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\src\main\java\com\itheima\UserService.java`
  - `public class UserService {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\src\test\java\com\itheima\UserServiceAiTest.java`
  - `public class UserServiceAiTest {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\src\test\java\com\itheima\UserServiceTest(1).java`
  - `public class UserServiceTest {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project01\src\test\java\com\itheima\UserServiceTest.java`
  - `public class UserServiceTest {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project02\pom.xml`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project02\src\main\java\com\itheima\HelloMaven.java`
  - `public class HelloMaven {`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project03\pom.xml`
- `ppt\03. 后端Web基础(Maven基础)\代码\maven-project03\src\main\java\com\itheima\HelloMaven.java`
  - `public class HelloMaven {`
