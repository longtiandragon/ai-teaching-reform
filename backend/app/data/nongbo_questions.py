"""
农宝系统后台管理项目 —— 真实代码练习题库。
基于 农宝后台管理系统项目1-5 的实际工程代码编写。
每个任务 4-6 道题，覆盖选择/判断/简答/代码填空。
"""

from backend.app.models import Question, QuestionOption

COURSE_ID = "nongbo-admin-project"


def A(text: str) -> QuestionOption:
    return QuestionOption(key="A", text=text)

def B(text: str) -> QuestionOption:
    return QuestionOption(key="B", text=text)

def C(text: str) -> QuestionOption:
    return QuestionOption(key="C", text=text)

def D(text: str) -> QuestionOption:
    return QuestionOption(key="D", text=text)

TF_OPTIONS = [A("正确"), B("错误")]


# ============================================================
# 任务 1：需求理解
# ============================================================
T1_REQUIREMENT: list[Question] = [
    Question(
        id="nongbo-req-001",
        course_id=COURSE_ID,
        lesson_id="task-requirement-understanding",
        type="single_choice",
        stem="农宝系统的知识管理模块需要维护哪两类内容实体？",
        options=[
            A("农业专家和图文课程"),
            B("农产品和农贸市场"),
            C("补贴政策和信贷信息"),
            D("广告和农事服务"),
        ],
        answer="A",
        explanation="知识管理模块的核心是 nb_expert（专家表）和 nb_graphic_course（图文课程表），以及 nb_video_course（视频课程表）。",
        difficulty="easy",
        tags=["需求分析", "知识管理"],
    ),
    Question(
        id="nongbo-req-002",
        course_id=COURSE_ID,
        lesson_id="task-requirement-understanding",
        type="single_choice",
        stem="农宝系统的 nb_service（农事服务）表中，category 字段的取值不包括以下哪项？",
        options=[
            A("supply（农资）"),
            B("machinery（农机）"),
            C("education（教育）"),
            D("finance（金融）"),
        ],
        answer="C",
        explanation="category 字段取值为：supply农资、machinery农机、tech技术、logistics物流、finance金融。不包含 education。",
        difficulty="medium",
        tags=["数据库设计", "农事服务"],
    ),
    Question(
        id="nongbo-req-003",
        course_id=COURSE_ID,
        lesson_id="task-requirement-understanding",
        type="true_false",
        stem="农宝系统的登录认证采用了 JWT Token + Spring Security 方案。",
        options=TF_OPTIONS,
        answer="B",
        explanation="实际实现是明文密码比对 + 随机 UUID 作为 Token，没有使用 JWT 也没有 Spring Security。",
        difficulty="easy",
        tags=["登录认证", "安全"],
    ),
    Question(
        id="nongbo-req-004",
        course_id=COURSE_ID,
        lesson_id="task-requirement-understanding",
        type="short_answer",
        stem="请列出农宝系统后台管理需要维护的 5 个以上业务模块名称。",
        answer="知识管理（专家+课程）、补贴政策、信贷信息、农事服务、农产品管理、农贸市场、广告管理",
        explanation="系统包含 8 个以上业务模块，需要学生从需求文档中提取。",
        difficulty="medium",
        tags=["需求分析", "业务模块"],
    ),
]


# ============================================================
# 任务 2：数据库设计
# ============================================================
T2_DATABASE: list[Question] = [
    Question(
        id="nongbo-db-001",
        course_id=COURSE_ID,
        lesson_id="task-course-table-design",
        type="single_choice",
        stem="nb_expert（专家表）中用于存储专家简介的字段类型是什么？",
        options=[
            A("VARCHAR(500)"),
            B("TEXT"),
            C("LONGTEXT"),
            D("BLOB"),
        ],
        answer="C",
        explanation="introduction 字段使用 LONGTEXT 类型，因为专家简介可能包含大量文字。",
        difficulty="easy",
        tags=["数据库设计", "字段类型"],
    ),
    Question(
        id="nongbo-db-002",
        course_id=COURSE_ID,
        lesson_id="task-course-table-design",
        type="single_choice",
        stem="nb_graphic_course 表中，用于区分「已发布」和「未发布」课程的字段是？",
        options=[
            A("status"),
            B("publish_status（0未发布/1已发布）"),
            C("del_flag"),
            D("recommend"),
        ],
        answer="B",
        explanation="publish_status 字段：0 表示未发布，1 表示已发布。与 del_flag（删除标记）和 recommend（推荐标记）不同。",
        difficulty="easy",
        tags=["数据库设计", "状态字段"],
    ),
    Question(
        id="nongbo-db-003",
        course_id=COURSE_ID,
        lesson_id="task-course-table-design",
        type="code_fill",
        stem="请补全建表 SQL，为 nb_expert 表添加专业领域和状态的联合索引：\n\nCREATE INDEX idx_specialty_status ON nb_expert(______, ______);",
        answer="specialty, status",
        explanation="根据实际表结构，idx_specialty_status 索引建立在 specialty 和 status 两个字段上。",
        difficulty="medium",
        tags=["数据库设计", "索引"],
    ),
    Question(
        id="nongbo-db-004",
        course_id=COURSE_ID,
        lesson_id="task-course-table-design",
        type="short_answer",
        stem="请说明 nb_farm_produce（农产品表）和 nb_farm_market（农贸市场表）之间的业务关系。",
        answer="农产品通过某种归属关系（如供应商/区域）关联到农贸市场。农贸市场是农产品的销售场所，一个市场可以有多个农产品供应商。",
        explanation="需要学生理解业务实体之间的关系设计。",
        difficulty="hard",
        tags=["数据库设计", "表关系"],
    ),
    Question(
        id="nongbo-db-005",
        course_id=COURSE_ID,
        lesson_id="task-course-table-design",
        type="true_false",
        stem="农宝系统所有业务表都使用 VARCHAR(50) 类型的 id 字段作为主键，而不是自增整数。",
        options=TF_OPTIONS,
        answer="A",
        explanation="除 nb_farm_market 使用 int 自增主键外，其他业务表都使用 VARCHAR(50) 类型的 id（UUID 生成）。",
        difficulty="medium",
        tags=["数据库设计", "主键策略"],
    ),
]


# ============================================================
# 任务 3：实体类开发
# ============================================================
T3_ENTITY: list[Question] = [
    Question(
        id="nongbo-entity-001",
        course_id=COURSE_ID,
        lesson_id="task-entity-design",
        type="single_choice",
        stem="在 Spring Boot 版本的农宝项目中，实体类继承的基类是什么？",
        options=[
            A("Serializable"),
            B("BaseEntity（包含公共字段 create_by, create_time 等）"),
            C("AbstractEntity"),
            D("Model"),
        ],
        answer="B",
        explanation="所有业务实体类继承 BaseEntity，该基类包含 create_by、create_time、update_by、update_time 等公共字段。",
        difficulty="easy",
        tags=["实体类", "继承"],
    ),
    Question(
        id="nongbo-entity-002",
        course_id=COURSE_ID,
        lesson_id="task-entity-design",
        type="code_fill",
        stem="请补全 Expert 实体类的 MyBatis-Plus 注解：\n\n@______\npublic class Expert extends BaseEntity {\n    @______(value = \"id\", type = IdType.ASSIGN_UUID)\n    private String id;\n    private String name;\n    private String specialty;\n}",
        answer="@TableName(\"nb_expert\")\n@TableId(value = \"id\", type = IdType.ASSIGN_UUID)",
        explanation="@TableName 指定表名，@TableId 指定主键字段和生成策略（UUID）。",
        difficulty="medium",
        tags=["MyBatis-Plus", "注解"],
    ),
    Question(
        id="nongbo-entity-003",
        course_id=COURSE_ID,
        lesson_id="task-entity-design",
        type="single_choice",
        stem="MyBatis-Plus 的 @TableField(fill = FieldFill.INSERT) 注解的作用是什么？",
        options=[
            A("标记该字段为数据库主键"),
            B("在插入数据时自动填充该字段（如 create_time）"),
            C("标记该字段不需要映射到数据库"),
            D("设置字段的默认值"),
        ],
        answer="B",
        explanation="FieldFill.INSERT 表示仅在插入时自动填充，FieldFill.INSERT_UPDATE 表示插入和更新时都填充。",
        difficulty="medium",
        tags=["MyBatis-Plus", "自动填充"],
    ),
    Question(
        id="nongbo-entity-004",
        course_id=COURSE_ID,
        lesson_id="task-entity-design",
        type="short_answer",
        stem="请写出 nb_service（农事服务）实体类中至少 5 个业务字段及其对应的 Java 类型。",
        answer="title(String), category(String), provider(String), phone(String), price(BigDecimal), status(Integer), address(String), order_count(Integer), rating(BigDecimal)",
        explanation="需要学生根据数据库表结构映射出 Java 字段类型。",
        difficulty="medium",
        tags=["实体类", "字段映射"],
    ),
]


# ============================================================
# 任务 4：Mapper/Service/Controller 开发
# ============================================================
T4_MVC: list[Question] = [
    Question(
        id="nongbo-mvc-001",
        course_id=COURSE_ID,
        lesson_id="task-mapper-service-controller",
        type="single_choice",
        stem="在 Spring Boot 版本中，Mapper 接口继承什么基类可以自动获得 CRUD 方法？",
        options=[
            A(" JpaRepository<T>"),
            B(" BaseMapper<T>"),
            C(" CrudRepository<T>"),
            D(" Dao<T>"),
        ],
        answer="B",
        explanation="MyBatis-Plus 的 BaseMapper<T> 提供了 insert、deleteById、updateById、selectById 等 17 个基础 CRUD 方法。",
        difficulty="easy",
        tags=["MyBatis-Plus", "Mapper"],
    ),
    Question(
        id="nongbo-mvc-002",
        course_id=COURSE_ID,
        lesson_id="task-mapper-service-controller",
        type="code_fill",
        stem="请补全 Service 层代码，实现分页查询专家列表：\n\npublic Result queryExpertList(PageQuery pageQuery, Expert expert) {\n    Page<Expert> page = new Page<>(pageQuery.getPageNum(), pageQuery.getPageSize());\n    LambdaQueryWrapper<Expert> wrapper = new LambdaQueryWrapper<>();\n    wrapper.like(StringUtils.isNotBlank(expert.getName()), ______::getName, expert.getName());\n    wrapper.eq(expert.getStatus() != null, ______::getStatus, expert.getStatus());\n    Page<Expert> result = expertMapper.selectPage(page, wrapper);\n    return Result.success(result.getRecords(), result.getTotal());\n}",
        answer="Expert\nExpert",
        explanation="LambdaQueryWrapper 使用方法引用（ClassName::getFieldName）来指定查询条件字段。",
        difficulty="medium",
        tags=["MyBatis-Plus", "分页查询"],
    ),
    Question(
        id="nongbo-mvc-003",
        course_id=COURSE_ID,
        lesson_id="task-mapper-service-controller",
        type="single_choice",
        stem="Controller 层使用什么注解来处理 RESTful 的 PUT 更新请求？",
        options=[
            A("@PostMapping"),
            B("@GetMapping"),
            C("@PutMapping"),
            D("@RequestMapping(method = PUT)"),
        ],
        answer="C",
        explanation="@PutMapping 是 @RequestMapping(method = RequestMethod.PUT) 的简写形式。",
        difficulty="easy",
        tags=["Spring MVC", "注解"],
    ),
    Question(
        id="nongbo-mvc-004",
        course_id=COURSE_ID,
        lesson_id="task-mapper-service-controller",
        type="short_answer",
        stem="请写出农宝系统中统一响应类 Result<T> 的基本结构（包含哪些字段），并说明 code=200 和 code=500 分别代表什么。",
        answer="Result<T> 包含 code(int 状态码), msg(String 提示信息), data(T 数据), total(Long 总记录数), rows(List 列表数据)。code=200 表示操作成功，code=500 表示操作失败。",
        explanation="统一响应格式是前后端分离项目的标准实践。",
        difficulty="easy",
        tags=["统一响应", "Result"],
    ),
    Question(
        id="nongbo-mvc-005",
        course_id=COURSE_ID,
        lesson_id="task-mapper-service-controller",
        type="code_fill",
        stem="请补全删除接口的 Controller 代码：\n\n@DeleteMapping(\"/expert/{ids}\")\npublic Result deleteExpert(@______ String ids) {\n    String[] idArray = ids.split(\",\");\n    for (String id : idArray) {\n        expertService.______(id);\n    }\n    return Result.success();\n}",
        answer="@PathVariable\nremoveById(id)",
        explanation="@PathVariable 从 URL 路径中提取参数，removeById 是 MyBatis-Plus IService 提供的删除方法。",
        difficulty="medium",
        tags=["Spring MVC", "批量删除"],
    ),
]


# ============================================================
# 任务 5：接口测试与学习总结
# ============================================================
T5_TEST: list[Question] = [
    Question(
        id="nongbo-test-001",
        course_id=COURSE_ID,
        lesson_id="task-api-test-reflection",
        type="single_choice",
        stem="使用 Postman 测试 POST 新增接口时，请求头应该设置什么？",
        options=[
            A("Content-Type: text/html"),
            B("Content-Type: application/json"),
            C("Content-Type: multipart/form-data"),
            D("不需要设置"),
        ],
        answer="B",
        explanation="前后端分离项目中，POST 请求通常使用 JSON 格式传递数据，需要设置 Content-Type: application/json。",
        difficulty="easy",
        tags=["接口测试", "Postman"],
    ),
    Question(
        id="nongbo-test-002",
        course_id=COURSE_ID,
        lesson_id="task-api-test-reflection",
        type="single_choice",
        stem="跨域问题的根本原因是什么？",
        options=[
            A("后端代码有 bug"),
            B("浏览器的同源策略限制了不同域名/端口的请求"),
            C("数据库连接失败"),
            D("前端代码语法错误"),
        ],
        answer="B",
        explanation="浏览器的同源策略（Same-Origin Policy）限制了从一个源（协议+域名+端口）向另一个源发起请求。前端 5173 端口访问后端 8081 端口就属于跨域。",
        difficulty="easy",
        tags=["跨域", "CORS"],
    ),
    Question(
        id="nongbo-test-003",
        course_id=COURSE_ID,
        lesson_id="task-api-test-reflection",
        type="short_answer",
        stem="请对比项目2（SSM版本）和项目3（Spring Boot版本）在以下三个方面的差异：1) 配置方式 2) SQL 编写方式 3) 分页实现方式。",
        answer="1) 配置：SSM 用 applicationContext.xml + web.xml，Spring Boot 用 application.yml + 注解。2) SQL：SSM 在 Mapper.xml 中手写 SQL，Spring Boot 用 MyBatis-Plus 自动生成。3) 分页：SSM 手写 LIMIT #{offset}, #{pageSize}，Spring Boot 用 Page 对象 + selectPage 方法。",
        explanation="这是项目迭代的核心对比，帮助学生理解技术演进。",
        difficulty="medium",
        tags=["技术对比", "SSM vs SpringBoot"],
    ),
    Question(
        id="nongbo-test-004",
        course_id=COURSE_ID,
        lesson_id="task-api-test-reflection",
        type="code_fill",
        stem="请补全 Spring Boot 项目的跨域配置类：\n\n@Configuration\npublic class CorsConfig implements WebMvcConfigurer {\n    @Override\n    public void addCorsMappings(CorsRegistry registry) {\n        registry.addMapping(\"/**\")\n                .allowedOrigins(\"______\")\n                .allowedMethods(\"GET\", \"POST\", \"PUT\", \"DELETE\", \"OPTIONS\")\n                .______(true);\n    }\n}",
        answer="*\nallowCredentials",
        explanation="allowedOrigins(\"*\") 允许所有来源，allowCredentials(true) 允许携带凭证信息。",
        difficulty="medium",
        tags=["跨域配置", "CORS"],
    ),
]


# ============================================================
# 编码实战题（需要学生真正写代码）
# ============================================================
CODE_EXERCISES: list[Question] = [
    # ── 模块1：需求分析 ──
    Question(
        id="nongbo-code-001",
        course_id=COURSE_ID,
        lesson_id="task-requirement-understanding",
        type="short_answer",
        stem="【编码题】请根据 nb_expert 表结构，编写建表 SQL（包含至少 8 个字段、2 个索引）。",
        answer="CREATE TABLE nb_expert (\n  id VARCHAR(50) PRIMARY KEY,\n  name VARCHAR(100) NOT NULL,\n  avatar LONGTEXT,\n  specialty VARCHAR(200),\n  title VARCHAR(100),\n  organization VARCHAR(200),\n  phone VARCHAR(20),\n  email VARCHAR(100),\n  introduction LONGTEXT,\n  service_count INT DEFAULT 0,\n  rating DECIMAL(3,1) DEFAULT 0.0,\n  status TINYINT DEFAULT 1,\n  create_by VARCHAR(50),\n  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,\n  update_by VARCHAR(50),\n  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n  remark VARCHAR(500),\n  INDEX idx_specialty (specialty),\n  INDEX idx_status (status)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
        explanation="需要包含 VARCHAR(50) 主键、LONGTEXT 类型字段、状态字段、公共字段、联合索引。",
        difficulty="medium",
        tags=["编码", "数据库设计", "建表SQL"],
    ),
    # ── 模块2：SSM 基础 ──
    Question(
        id="nongbo-code-002",
        course_id=COURSE_ID,
        lesson_id="task-ssm-mapper-xml",
        type="short_answer",
        stem="【编码题】请为 nb_expert 表编写 MyBatis Mapper.xml，实现：根据 id 查询、分页查询（支持 name 模糊搜索和 status 筛选）、插入、更新、删除。",
        answer='<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">\n<mapper namespace="org.nong.mapper.ExpertMapper">\n  <select id="selectById" parameterType="String" resultType="org.nong.entity.Expert">\n    SELECT * FROM nb_expert WHERE id = #{id}\n  </select>\n  <select id="selectList" parameterType="org.nong.common.PageQuery" resultType="org.nong.entity.Expert">\n    SELECT * FROM nb_expert\n    <where>\n      <if test="name != null and name != \'\'">AND name LIKE CONCAT(\'%\', #{name}, \'%\')</if>\n      <if test="status != null">AND status = #{status}</if>\n    </where>\n    ORDER BY create_time DESC\n    LIMIT #{offset}, #{pageSize}\n  </select>\n  <insert id="insert" parameterType="org.nong.entity.Expert">\n    INSERT INTO nb_expert(id, name, avatar, specialty, title, organization, phone, email, introduction, status, create_by, create_time)\n    VALUES(#{id}, #{name}, #{avatar}, #{specialty}, #{title}, #{organization}, #{phone}, #{email}, #{introduction}, #{status}, #{createBy}, NOW())\n  </insert>\n  <update id="update" parameterType="org.nong.entity.Expert">\n    UPDATE nb_expert\n    <set>\n      <if test="name != null">name = #{name},</if>\n      <if test="specialty != null">specialty = #{specialty},</if>\n      <if test="status != null">status = #{status},</if>\n      update_time = NOW()\n    </set>\n    WHERE id = #{id}\n  </update>\n  <delete id="deleteById" parameterType="String">\n    DELETE FROM nb_expert WHERE id = #{id}\n  </delete>\n</mapper>',
        explanation="需要掌握动态 SQL（if/where/set）、模糊搜索 CONCAT、分页 LIMIT、参数占位符 #{}。",
        difficulty="hard",
        tags=["编码", "MyBatis", "Mapper XML", "动态SQL"],
    ),
    # ── 模块3：Spring Boot 知识管理 ──
    Question(
        id="nongbo-code-003",
        course_id=COURSE_ID,
        lesson_id="task-expert-crud",
        type="short_answer",
        stem="【编码题】请编写 ExpertController 的完整代码，包含：分页列表查询（GET /list）、查看详情（GET /{id}）、新增（POST）、修改（PUT）、批量删除（DELETE /{ids}）。使用 Spring Boot + MyBatis-Plus 风格。",
        answer='@RestController\n@RequestMapping("/dev-api/yjnb/expert")\npublic class ExpertController {\n    @Autowired\n    private IExpertService expertService;\n\n    @GetMapping("/list")\n    public Result list(PageQuery pageQuery, Expert expert) {\n        Page<Expert> page = new Page<>(pageQuery.getPageNum(), pageQuery.getPageSize());\n        LambdaQueryWrapper<Expert> wrapper = new LambdaQueryWrapper<>();\n        wrapper.like(StringUtils.isNotBlank(expert.getName()), Expert::getName, expert.getName());\n        wrapper.eq(expert.getStatus() != null, Expert::getStatus, expert.getStatus());\n        wrapper.orderByDesc(Expert::getCreateTime);\n        Page<Expert> result = expertService.page(page, wrapper);\n        return Result.success(result.getRecords(), result.getTotal());\n    }\n\n    @GetMapping("/{id}")\n    public Result getById(@PathVariable String id) {\n        return Result.success(expertService.getById(id));\n    }\n\n    @PostMapping\n    public Result add(@RequestBody Expert expert) {\n        expert.setId(IdUtil.fastSimpleUUID());\n        expertService.save(expert);\n        return Result.success();\n    }\n\n    @PutMapping\n    public Result update(@RequestBody Expert expert) {\n        expertService.updateById(expert);\n        return Result.success();\n    }\n\n    @DeleteMapping("/{ids}")\n    public Result delete(@PathVariable String ids) {\n        for (String id : ids.split(",")) {\n            expertService.removeById(id);\n        }\n        return Result.success();\n    }\n}',
        explanation="需要掌握 @RestController、@RequestMapping、LambdaQueryWrapper 分页查询、@PathVariable 批量删除、Result 统一返回。",
        difficulty="hard",
        tags=["编码", "Spring Boot", "Controller", "MyBatis-Plus"],
    ),
    Question(
        id="nongbo-code-004",
        course_id=COURSE_ID,
        lesson_id="task-course-management",
        type="short_answer",
        stem="【编码题】请编写图文课程的发布/取消发布接口，要求：传入课程 id 和 publish_status（0或1），更新数据库中的 publish_status 和 publish_time 字段。",
        answer='@PutMapping("/publish/{id}/{status}")\npublic Result updatePublishStatus(@PathVariable String id, @PathVariable Integer status) {\n    GraphicCourse course = new GraphicCourse();\n    course.setId(id);\n    course.setPublishStatus(status);\n    if (status == 1) {\n        course.setPublishTime(LocalDateTime.now());\n    }\n    graphicCourseService.updateById(course);\n    return Result.success();\n}',
        explanation="需要理解状态切换逻辑：发布时记录时间，取消发布时只更新状态。",
        difficulty="medium",
        tags=["编码", "状态管理", "RESTful"],
    ),
    # ── 模块4：进阶业务 ──
    Question(
        id="nongbo-code-005",
        course_id=COURSE_ID,
        lesson_id="task-service-module",
        type="short_answer",
        stem="【编码题】请编写农事服务的分页查询接口，要求：支持按 category（分类）和 status（上下架状态）筛选，支持按 price 排序。",
        answer='@GetMapping("/list")\npublic Result list(PageQuery pageQuery, NongboService service) {\n    Page<NongboService> page = new Page<>(pageQuery.getPageNum(), pageQuery.getPageSize());\n    LambdaQueryWrapper<NongboService> wrapper = new LambdaQueryWrapper<>();\n    wrapper.like(StringUtils.isNotBlank(service.getTitle()), NongboService::getTitle, service.getTitle());\n    wrapper.eq(StringUtils.isNotBlank(service.getCategory()), NongboService::getCategory, service.getCategory());\n    wrapper.eq(service.getStatus() != null, NongboService::getStatus, service.getStatus());\n    wrapper.orderByAsc(NongboService::getPrice);\n    Page<NongboService> result = nongboServiceService.page(page, wrapper);\n    return Result.success(result.getRecords(), result.getTotal());\n}',
        explanation="需要掌握多条件筛选 + 排序的 LambdaQueryWrapper 写法。",
        difficulty="medium",
        tags=["编码", "分页查询", "条件筛选"],
    ),
    # ── 模块5：前端联调 ──
    Question(
        id="nongbo-code-006",
        course_id=COURSE_ID,
        lesson_id="task-frontend-integration",
        type="short_answer",
        stem="【编码题】请编写 Vue 3 + Element Plus 的专家列表页面模板，要求包含：搜索表单（名称输入+状态选择+搜索按钮）、数据表格（姓名/专业/职称/状态/操作列）、分页组件。",
        answer='<template>\n  <div>\n    <el-form :inline="true" :model="queryParams">\n      <el-form-item label="姓名">\n        <el-input v-model="queryParams.name" placeholder="请输入姓名" />\n      </el-form-item>\n      <el-form-item label="状态">\n        <el-select v-model="queryParams.status" placeholder="请选择">\n          <el-option label="可用" :value="1" />\n          <el-option label="不可用" :value="0" />\n        </el-select>\n      </el-form-item>\n      <el-form-item>\n        <el-button type="primary" @click="handleQuery">搜索</el-button>\n      </el-form-item>\n    </el-form>\n\n    <el-table :data="tableData" border>\n      <el-table-column prop="name" label="姓名" />\n      <el-table-column prop="specialty" label="专业领域" />\n      <el-table-column prop="title" label="职称" />\n      <el-table-column prop="status" label="状态">\n        <template #default="{ row }">\n          <el-tag :type="row.status === 1 ? \'success\' : \'danger\'">\n            {{ row.status === 1 ? \'可用\' : \'不可用\' }}\n          </el-tag>\n        </template>\n      </el-table-column>\n      <el-table-column label="操作">\n        <template #default="{ row }">\n          <el-button size="small" @click="handleEdit(row)">编辑</el-button>\n          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>\n        </template>\n      </el-table-column>\n    </el-table>\n\n    <el-pagination\n      v-model:current-page="queryParams.pageNum"\n      v-model:page-size="queryParams.pageSize"\n      :total="total"\n      layout="total, prev, pager, next"\n      @current-change="getList"\n    />\n  </div>\n</template>',
        explanation="需要掌握 el-form/el-table/el-pagination 组件、插槽自定义列、v-model 双向绑定。",
        difficulty="hard",
        tags=["编码", "Vue 3", "Element Plus", "前端"],
    ),
    Question(
        id="nongbo-code-007",
        course_id=COURSE_ID,
        lesson_id="task-frontend-integration",
        type="short_answer",
        stem="【编码题】请编写 Axios 请求封装（request.ts），要求：创建实例设置 baseURL 和超时、请求拦截器自动添加 Token、响应拦截器处理错误、导出 get/post/put/del 方法。",
        answer='import axios from "axios";\nimport { ElMessage } from "element-plus";\n\nconst request = axios.create({\n  baseURL: "/dev-api",\n  timeout: 10000,\n});\n\nrequest.interceptors.request.use((config) => {\n  const token = localStorage.getItem("token");\n  if (token) config.headers.Authorization = `Bearer ${token}`;\n  return config;\n});\n\nrequest.interceptors.response.use(\n  (response) => {\n    const res = response.data;\n    if (res.code !== 200) {\n      ElMessage.error(res.msg || "请求失败");\n      return Promise.reject(new Error(res.msg));\n    }\n    return res;\n  },\n  (error) => {\n    ElMessage.error(error.message || "网络错误");\n    return Promise.reject(error);\n  }\n);\n\nexport const get = (url, params) => request.get(url, { params });\nexport const post = (url, data) => request.post(url, data);\nexport const put = (url, data) => request.put(url, data);\nexport const del = (url) => request.delete(url);\nexport default request;',
        explanation="需要掌握 Axios 实例创建、请求/响应拦截器、Token 注入、错误处理、统一导出。",
        difficulty="medium",
        tags=["编码", "Axios", "TypeScript", "请求封装"],
    ),
    Question(
        id="nongbo-code-008",
        course_id=COURSE_ID,
        lesson_id="task-data-dashboard",
        type="short_answer",
        stem="【编码题】请编写后端统计接口，返回各业务模块的记录数量（专家数、课程数、服务数），SQL 使用 COUNT + GROUP BY。",
        answer='@GetMapping("/overview")\npublic Result overview() {\n    Map<String, Object> data = new HashMap<>();\n    data.put("expertCount", expertMapper.selectCount(null));\n    data.put("courseCount", graphicCourseMapper.selectCount(null));\n    data.put("serviceCount", serviceMapper.selectCount(null));\n    data.put("policyCount", policyMapper.selectCount(null));\n    data.put("produceCount", produceMapper.selectCount(null));\n    return Result.success(data);\n}\n\n// 或者使用一条 SQL：\n// SELECT \'expert\' as type, COUNT(*) as cnt FROM nb_expert\n// UNION ALL\n// SELECT \'course\', COUNT(*) FROM nb_graphic_course\n// UNION ALL\n// SELECT \'service\', COUNT(*) FROM nb_service',
        explanation="需要掌握 MyBatis-Plus 的 selectCount 方法或 SQL UNION ALL 聚合查询。",
        difficulty="medium",
        tags=["编码", "统计查询", "聚合函数"],
    ),
]


# ============================================================
# 全部农宝项目种子题合并
# ============================================================
NONGBO_SEED_QUESTIONS: list[Question] = (
    T1_REQUIREMENT + T2_DATABASE + T3_ENTITY + T4_MVC + T5_TEST + CODE_EXERCISES
)


def nongbo_questions_by_lesson(lesson_id: str) -> list[Question]:
    return [q for q in NONGBO_SEED_QUESTIONS if q.lesson_id == lesson_id]


def nongbo_questions_by_course(course_id: str) -> list[Question]:
    return [q for q in NONGBO_SEED_QUESTIONS if q.course_id == course_id]
