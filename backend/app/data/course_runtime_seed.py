from __future__ import annotations

from backend.app.data.courses import NONGBO_COURSE_ID, SPRINGBOOT_COURSE_ID, get_lessons


NONGBO_RUNTIME_SEED = {
    "courseLine": {
        "slug": NONGBO_COURSE_ID,
        "title": "农宝系统后台管理项目实训",
        "description": "基于农宝智慧助农管理系统的真实需求、数据库、接口文档和源码，按 5 个迭代阶段引导学生完成 Spring Boot 后端开发。",
        "targetAudience": "软件技术专业 Web 应用系统开发课程学生",
        "techStack": ["Spring Boot 3.0", "MyBatis-Plus 3.5", "MySQL 8.0", "RESTful API", "Vue 3", "Element Plus"],
        "status": "active",
    },
    "modules": [
        # ─── 模块 1：需求分析与技术方案（对应项目1）───
        {
            "slug": "nongbo-m1-requirements",
            "title": "模块1：需求分析与技术方案",
            "description": "读懂农宝系统业务需求，梳理后台管理需要维护的模块和数据实体。",
            "businessContext": "农宝系统面向农业服务场景，后台需要维护专家、课程、补贴政策、信贷信息、农事服务、农产品、农贸市场、广告等业务数据。",
            "tasks": [
                {
                    "slug": "task-requirement-understanding",
                    "title": "业务需求梳理",
                    "type": "analysis",
                    "goal": "理解农宝系统后台管理的整体业务范围，列出需要维护的核心模块。",
                    "scenario": "你正在接手农宝智慧助农管理系统的后台开发，需要先理解系统要管理哪些内容。",
                    "instruction": "请根据需求文档，用自己的话说明后台管理系统至少需要哪些业务模块，每个模块管理什么数据。不要写代码。",
                    "requiredArtifactType": "text",
                    "difficulty": 1,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "concept",
                            "name": "模块识别",
                            "weight": 50,
                            "required": True,
                            "config": {
                                "concepts": ["专家管理", "课程管理", "补贴政策", "信贷信息", "农事服务", "农产品", "农贸市场", "广告"],
                                "minHit": 5,
                            },
                        },
                        {
                            "type": "rag_grounded",
                            "name": "需求依据",
                            "weight": 30,
                            "required": True,
                            "config": {"minEvidence": 1},
                        },
                        {
                            "type": "anti_shortcut",
                            "name": "独立思考",
                            "weight": 20,
                            "required": False,
                            "config": {"forbiddenPatterns": ["完整项目", "所有文件", "一键生成"]},
                        },
                    ],
                },
                {
                    "slug": "task-database-overview",
                    "title": "数据库表结构分析",
                    "type": "analysis",
                    "goal": "理解 nb_database 中 12 张表的结构和表间关系。",
                    "scenario": "系统使用 MySQL 数据库，包含系统基础表（sys_user, sys_role, sys_config）和业务表（nb_expert, nb_graphic_course 等）。",
                    "instruction": "请列出至少 6 张业务表的核心字段，并说明表与表之间的业务关系。",
                    "requiredArtifactType": "text",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "表名识别",
                            "weight": 40,
                            "required": True,
                            "config": {
                                "keywords": ["nb_expert", "nb_graphic_course", "nb_video_course", "nb_allowance_policy", "nb_credit_loan", "nb_service", "nb_farm_produce", "nb_farm_market", "nb_advertisement"],
                                "minHit": 6,
                            },
                        },
                        {
                            "type": "concept",
                            "name": "字段理解",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["主键", "状态字段", "时间字段", "外键关联", "LONGTEXT"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "依据数据库文档",
                            "weight": 25,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
            ],
        },
        # ─── 模块 2：SSM 后端基础（对应项目2）───
        {
            "slug": "nongbo-m2-ssm-basics",
            "title": "模块2：SSM 后端基础功能",
            "description": "理解传统 SSM（Spring + Spring MVC + MyBatis）架构，完成 XML 配置和手写 SQL。",
            "businessContext": "项目2 使用传统 SSM 架构，WAR 包部署到 Tomcat，手写 Mapper.xml SQL，需要理解 IOC/DI、AOP、事务等核心概念。",
            "tasks": [
                {
                    "slug": "task-ssm-config",
                    "title": "SSM 配置文件理解",
                    "type": "analysis",
                    "goal": "理解 applicationContext.xml、web.xml、spring-mvc.xml 的作用和配置项。",
                    "scenario": "项目2 使用 XML 配置方式搭建 SSM 环境，需要读懂每个配置文件的职责。",
                    "instruction": "请说明三个核心配置文件各自负责什么，列出至少 3 个关键配置项及其作用。",
                    "requiredArtifactType": "text",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "concept",
                            "name": "配置职责",
                            "weight": 50,
                            "required": True,
                            "config": {"concepts": ["IOC 容器", "组件扫描", "视图解析器", "数据源", "事务管理", "DispatcherServlet"], "minHit": 4},
                        },
                        {
                            "type": "keyword",
                            "name": "配置项",
                            "weight": 30,
                            "required": True,
                            "config": {"keywords": ["applicationContext", "web.xml", "spring-mvc", "DataSource", "SqlSessionFactory", "ComponentScan"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目文件依据",
                            "weight": 20,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-ssm-mapper-xml",
                    "title": "Mapper XML 手写 SQL",
                    "type": "coding",
                    "goal": "手写 MyBatis Mapper.xml，完成专家表的增删改查 SQL。",
                    "scenario": "项目2 的 Mapper 层需要手写 XML SQL，不使用 MyBatis-Plus 自动生成。",
                    "instruction": "请为 nb_expert 表编写 Mapper.xml 的 selectById、insert、update、delete 四个 SQL 语句。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "SQL 语法",
                            "weight": 40,
                            "required": True,
                            "config": {"keywords": ["SELECT", "INSERT INTO", "UPDATE", "DELETE FROM", "WHERE", "id = #{"], "minHit": 5},
                        },
                        {
                            "type": "concept",
                            "name": "MyBatis 映射",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["parameterType", "resultType", "动态SQL", "占位符"], "minHit": 2},
                        },
                        {
                            "type": "anti_shortcut",
                            "name": "手写能力",
                            "weight": 25,
                            "required": False,
                            "config": {"forbiddenPatterns": ["MyBatis-Plus", "BaseMapper", "自动生成"]},
                        },
                    ],
                },
            ],
        },
        # ─── 模块 3：Spring Boot 知识管理（对应项目3）───
        {
            "slug": "nongbo-m3-knowledge-management",
            "title": "模块3：Spring Boot 知识管理模块",
            "description": "使用 Spring Boot + MyBatis-Plus 完成专家管理和图文课程管理的 CRUD。",
            "businessContext": "项目3 迭代到 Spring Boot 架构，使用 MyBatis-Plus 简化 CRUD，需要完成 nb_expert 和 nb_graphic_course 的完整接口。",
            "tasks": [
                {
                    "slug": "task-springboot-setup",
                    "title": "Spring Boot 项目搭建",
                    "type": "coding",
                    "goal": "理解 Spring Boot 项目的包结构和核心配置。",
                    "scenario": "项目3 从 SSM 迁移到 Spring Boot，配置方式从 XML 变为 application.yml + 注解。",
                    "instruction": "请说明 Spring Boot 项目的包结构（controller/service/mapper/entity/common/config），以及 application.yml 中需要配置哪些内容。",
                    "requiredArtifactType": "text",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "concept",
                            "name": "分层架构",
                            "weight": 45,
                            "required": True,
                            "config": {"concepts": ["Controller", "Service", "Mapper", "Entity", "Common", "Config", "分层职责"], "minHit": 5},
                        },
                        {
                            "type": "keyword",
                            "name": "配置项",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["server.port", "spring.datasource", "mybatis-plus", "application.yml"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目代码依据",
                            "weight": 20,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-expert-crud",
                    "title": "专家管理 CRUD 开发",
                    "type": "coding",
                    "goal": "完成 nb_expert 表的完整增删改查接口。",
                    "scenario": "专家管理需要：分页列表查询（支持按名称/专业筛选）、查看详情、新增、修改、批量删除。",
                    "instruction": "请提交 Expert 实体类、ExpertMapper 接口、ExpertService 关键方法、ExpertController 的 RESTful 接口代码片段。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "MyBatis-Plus 注解",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["@TableName", "@TableId", "@TableField", "BaseMapper", "IService", "ServiceImpl"], "minHit": 4},
                        },
                        {
                            "type": "concept",
                            "name": "CRUD 完整性",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["分页查询", "条件筛选", "新增", "修改", "删除", "统一返回"], "minHit": 4},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目接口规范",
                            "weight": 30,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-course-management",
                    "title": "图文课程管理开发",
                    "type": "coding",
                    "goal": "完成 nb_graphic_course 表的 CRUD，包含发布状态和推荐功能。",
                    "scenario": "图文课程需要支持发布/取消发布、推荐/取消推荐、按分类筛选等操作。",
                    "instruction": "请提交课程管理的关键接口代码，特别说明 publish_status 和 recommend 字段的处理逻辑。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "状态管理",
                            "weight": 40,
                            "required": True,
                            "config": {"keywords": ["publish_status", "recommend", "status", "LambdaQueryWrapper", "update"], "minHit": 4},
                        },
                        {
                            "type": "concept",
                            "name": "业务逻辑",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["发布状态切换", "推荐标记", "分页查询", "条件构造器"], "minHit": 3},
                        },
                        {
                            "type": "code_pattern",
                            "name": "代码规范",
                            "weight": 25,
                            "required": False,
                            "config": {"patterns": ["@RestController", "@RequestMapping", "Result.success"]},
                        },
                    ],
                },
            ],
        },
        # ─── 模块 4：进阶业务模块（对应项目4）───
        {
            "slug": "nongbo-m4-advanced-modules",
            "title": "模块4：补贴政策/信贷/农事服务",
            "description": "在知识管理基础上，扩展补贴政策、信贷信息和农事服务三个业务模块。",
            "businessContext": "项目4 在项目3 基础上新增三个模块，复用相同的分层模式和 CRUD 模板。",
            "tasks": [
                {
                    "slug": "task-policy-module",
                    "title": "补贴政策模块开发",
                    "type": "coding",
                    "goal": "完成 nb_allowance_policy 表的 CRUD 接口。",
                    "scenario": "补贴政策模块与图文课程结构类似，包含标题、作者、摘要、内容、图片、发布状态等字段。",
                    "instruction": "请提交补贴政策模块的 Controller 代码，并说明与课程管理模块的相似之处和可复用的部分。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "接口规范",
                            "weight": 40,
                            "required": True,
                            "config": {"keywords": ["@RestController", "@RequestMapping", "GET", "POST", "PUT", "DELETE", "Result"], "minHit": 5},
                        },
                        {
                            "type": "concept",
                            "name": "代码复用",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["模块复用", "分页查询", "CRUD 模板", "BaseEntity"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目代码依据",
                            "weight": 25,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-service-module",
                    "title": "农事服务模块开发",
                    "type": "coding",
                    "goal": "完成 nb_service 表的 CRUD，包含分类筛选和上下架功能。",
                    "scenario": "农事服务有 5 种分类（supply/machinery/tech/logistics/finance），需要支持按分类查询和上下架操作。",
                    "instruction": "请提交农事服务模块的关键代码，特别说明 category 字段的筛选逻辑和 status 字段的上下架处理。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "枚举筛选",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["category", "supply", "machinery", "tech", "logistics", "finance", "eq", "status"], "minHit": 5},
                        },
                        {
                            "type": "concept",
                            "name": "状态管理",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["上下架", "分类筛选", "价格字段", "BigDecimal"], "minHit": 3},
                        },
                        {
                            "type": "anti_shortcut",
                            "name": "独立编码",
                            "weight": 30,
                            "required": False,
                            "config": {"forbiddenPatterns": ["直接复制课程管理", "完全一样"]},
                        },
                    ],
                },
            ],
        },
        # ─── 模块 5：完整前后端对接（对应项目5）───
        {
            "slug": "nongbo-m5-fullstack",
            "title": "模块5：完整前后端对接",
            "description": "完成剩余模块（农产品、农贸市场、广告）并实现 Vue 前端联调。",
            "businessContext": "项目5 是完整版，包含全部业务模块和 Vue 3 前端，需要处理跨域、文件上传、数据统计等功能。",
            "tasks": [
                {
                    "slug": "task-produce-module",
                    "title": "农产品与农贸市场模块",
                    "type": "coding",
                    "goal": "完成 nb_farm_produce 和 nb_farm_market 的 CRUD 接口。",
                    "scenario": "农产品需要支持推荐和发布推送，农贸市场使用自增主键而非 UUID。",
                    "instruction": "请提交农产品模块的 Controller 代码，说明与之前模块的差异（如 push_status、recommend 字段处理）。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "新增字段",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["push_status", "recommend", "provider_name", "farm_market", "region_id"], "minHit": 3},
                        },
                        {
                            "type": "concept",
                            "name": "主键策略差异",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["UUID 主键", "自增主键", "IdType.ASSIGN_UUID", "IdType.AUTO"], "minHit": 2},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目代码依据",
                            "weight": 30,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-frontend-integration",
                    "title": "Vue 前端联调",
                    "type": "coding",
                    "goal": "实现 Vue 3 + Element Plus 前端页面与后端 API 的对接。",
                    "scenario": "前端使用 Axios 调用后端接口，需要处理跨域、Token 请求头、响应数据格式。",
                    "instruction": "请说明前端 request.ts 的封装方式（拦截器、Token、跨域），以及一个完整的列表页面（搜索+表格+分页+新增弹窗）的实现思路。",
                    "requiredArtifactType": "text",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "concept",
                            "name": "前后端对接",
                            "weight": 40,
                            "required": True,
                            "config": {"concepts": ["Axios", "请求拦截器", "响应拦截器", "Token", "跨域", "Element Plus"], "minHit": 4},
                        },
                        {
                            "type": "keyword",
                            "name": "前端技术栈",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["vue", "element-plus", "axios", "pinia", "vue-router", "el-table", "el-form"], "minHit": 4},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目前端代码依据",
                            "weight": 25,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-data-dashboard",
                    "title": "数据统计大屏",
                    "type": "coding",
                    "goal": "实现后端统计接口和前端 ECharts 数据可视化。",
                    "scenario": "管理后台需要数据概览，包括总记录数、分类统计、月度趋势等。",
                    "instruction": "请提交一个统计接口的实现思路（SQL 聚合查询 + Controller 返回），以及前端 ECharts 柱状图的渲染代码片段。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "统计 SQL",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["COUNT", "GROUP BY", "SUM", "AVG", "statistics", "overview"], "minHit": 3},
                        },
                        {
                            "type": "concept",
                            "name": "数据可视化",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["ECharts", "柱状图", "折线图", "饼图", "数据绑定"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目代码依据",
                            "weight": 30,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
            ],
        },
    ],
}


def springboot_runtime_seed() -> dict:
    lessons = get_lessons(SPRINGBOOT_COURSE_ID)
    return {
        "courseLine": {
            "slug": SPRINGBOOT_COURSE_ID,
            "title": "SpringBoot 12 讲课程闯关线",
            "description": "将 12 讲课程资料转为可检查、可记录的 AI 辅助学习任务。",
            "targetAudience": "Web 后端开发初学者",
            "techStack": ["Spring Boot", "MyBatis", "MySQL", "RESTful API"],
            "status": "active",
        },
        "modules": [
            {
                "slug": "springboot-foundation-path",
                "title": "SpringBoot 基础能力路线",
                "description": "按课程章节逐步完成知识理解、练习提交和复盘。",
                "businessContext": "课程资料来自 docs/course-materials，任务与每讲验收标准对齐。",
                "tasks": [
                    {
                        "slug": f"task-{lesson.id}",
                        "title": lesson.title,
                        "type": "lesson_practice",
                        "goal": "理解本讲核心知识点，并完成本讲练习的关键片段。",
                        "scenario": lesson.summary,
                        "instruction": lesson.practice.description or "请提交本讲练习的关键代码或说明。",
                        "requiredArtifactType": "code_or_text",
                        "difficulty": 1 + min(index // 4, 2),
                        "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                        "rubrics": [
                            {
                                "type": "concept",
                                "name": "课程目标覆盖",
                                "weight": 45,
                                "required": True,
                                "config": {"concepts": lesson.objectives[:6] or [lesson.title], "minHit": 1},
                            },
                            {
                                "type": "keyword",
                                "name": "验收关键词",
                                "weight": 35,
                                "required": True,
                                "config": {"keywords": _keywords_from_checklist(lesson.practice.checklist), "minHit": 2},
                            },
                            {
                                "type": "rag_grounded",
                                "name": "课程资料依据",
                                "weight": 20,
                                "required": False,
                                "config": {"minEvidence": 1},
                            },
                        ],
                    }
                    for index, lesson in enumerate(lessons)
                ],
            }
        ],
    }


def course_runtime_seeds() -> list[dict]:
    return [springboot_runtime_seed(), NONGBO_RUNTIME_SEED]


def _keywords_from_checklist(items: list[str]) -> list[str]:
    keywords: list[str] = []
    for item in items[:6]:
        for token in item.replace("，", " ").replace("。", " ").replace("/", " ").split():
            cleaned = token.strip("；;、,.()（）<>`")
            if len(cleaned) >= 2:
                keywords.append(cleaned)
    return keywords[:12] or ["Spring", "Boot", "代码", "说明"]
