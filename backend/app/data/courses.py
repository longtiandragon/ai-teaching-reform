import json
import re
from functools import lru_cache
from pathlib import Path

from backend.app.models import CourseSummary, LessonDetail, LessonSummary, PracticeTask


ROOT_DIR = Path(__file__).resolve().parents[3]
SPRINGBOOT_COURSE_ID = "springboot-course-12"
NONGBO_COURSE_ID = "nongbo-admin-project"
COURSE_ID = SPRINGBOOT_COURSE_ID

COURSE_MATERIALS_DIR = ROOT_DIR / "docs" / "course-materials"
COURSE_STANDARD_DOC = ROOT_DIR / "孙立晔+《Web系统应用开发一》+课程标准_24软.doc"
ROOT_NONGBO_SQL = ROOT_DIR / "nb_database.sql"
PROJECT_ROOT = ROOT_DIR / "农博后台管理系统项目1-5-20260609" / "农博后台管理系统项目1-5"
PROJECT_DOC_DIR = PROJECT_ROOT / "项目1-需求与技术方案"
PROJECT_BACKEND = PROJECT_ROOT / "项目5-完整前后端对接" / "nbspringproduct"
PROJECT_FRONTEND = PROJECT_ROOT / "项目5-完整前后端对接" / "nbvueproject"


def get_courses() -> list[CourseSummary]:
    return [get_course_summary(SPRINGBOOT_COURSE_ID), get_course_summary(NONGBO_COURSE_ID)]


def get_course_summary(course_id: str = COURSE_ID) -> CourseSummary:
    lessons = get_lessons(course_id)
    if course_id == NONGBO_COURSE_ID:
        return CourseSummary(
            id=NONGBO_COURSE_ID,
            title="农宝后台管理系统项目实训",
            subtitle="按《Web应用系统开发一》课程标准组织路线，落到真实农宝后台需求、数据库、接口和 SpringBoot/Vue 源码",
            progress=0,
            lessons=[_summary(lesson, index, "真实项目") for index, lesson in enumerate(lessons)],
        )
    return CourseSummary(
        id=SPRINGBOOT_COURSE_ID,
        title="SpringBoot 12 讲课程",
        subtitle="来自已整理 PPT Markdown 的后端 Web 与 SpringBoot 学习路径",
        progress=0,
        lessons=[_summary(lesson, index, "课程资料") for index, lesson in enumerate(lessons)],
    )


def get_lessons(course_id: str = COURSE_ID) -> list[LessonDetail]:
    courses = _course_map()
    return courses.get(course_id, courses[SPRINGBOOT_COURSE_ID])


def get_lesson(course_id: str | None = None, lesson_id: str | None = None) -> LessonDetail:
    if lesson_id is None and course_id and course_id not in _course_map():
        lesson_id = course_id
        course_id = COURSE_ID
    selected_course = course_id or COURSE_ID
    lessons = get_lessons(selected_course)
    if lesson_id is None:
        return lessons[0]
    for lesson in lessons:
        if lesson.id == lesson_id:
            return lesson
    return lessons[0]


def get_all_lessons() -> list[LessonDetail]:
    return [lesson for lessons in _course_map().values() for lesson in lessons]


@lru_cache
def _course_map() -> dict[str, list[LessonDetail]]:
    return {
        SPRINGBOOT_COURSE_ID: _build_springboot_lessons(),
        NONGBO_COURSE_ID: _build_nongbo_lessons(),
    }


def _summary(lesson: LessonDetail, index: int, source: str) -> LessonSummary:
    return LessonSummary(
        id=lesson.id,
        title=lesson.title,
        duration="按课堂安排",
        status="active" if index == 0 else "locked",
        tags=[source, "RAG", "真实资料"],
        source=lesson.source,
    )


def _build_springboot_lessons() -> list[LessonDetail]:
    manifest_path = COURSE_MATERIALS_DIR / "manifest.json"
    manifest = json.loads(_read_text(manifest_path) or '{"lessons":[]}')
    lessons: list[LessonDetail] = []
    for item in manifest.get("lessons", []):
        path = COURSE_MATERIALS_DIR / item["file"]
        content = _read_text(path)
        title = item.get("title") or _first_heading(content) or path.stem
        lesson_id = f"springboot-{item.get('slug') or path.stem}"
        objectives = _extract_bullets(content, "## 二、学习目标")
        practice_items = _extract_bullets(content, "## 六、课堂练习")
        checklist = _extract_bullets(content, "## 七、验收标准")
        source_lines = "\n".join(f"- {source}" for source in item.get("sources", []))
        code_index = _extract_section(content, "## 十一、配套代码索引", 1200)
        template = _springboot_practice_template(content, code_index)
        lessons.append(
            LessonDetail(
                id=lesson_id,
                course_id=SPRINGBOOT_COURSE_ID,
                title=title,
                summary=item.get("summary") or _plain_excerpt(content, 220),
                objectives=objectives or [_plain_excerpt(_extract_section(content, "## 四、核心知识点", 400), 120)],
                content="\n\n".join(
                    part
                    for part in [
                        _extract_section(content, "## 一、课堂定位", 900),
                        _extract_section(content, "## 四、核心知识点", 1200),
                        f"资料来源：\n{source_lines}" if source_lines else "",
                    ]
                    if part
                )
                or _plain_excerpt(content, 1800),
                practice=PracticeTask(
                    title=practice_items[0] if practice_items else f"{title} 课堂练习",
                    description="\n".join(practice_items) or _plain_excerpt(_extract_section(content, "## 六、课堂练习", 500), 260),
                    template=template,
                    checklist=checklist or ["能引用本讲资料说明实现依据", "提交可读代码或配置片段", "说明失败场景"],
                ),
                source=f"docs/course-materials/{item['file']}",
            )
        )
    return lessons


def _build_nongbo_lessons_legacy() -> list[LessonDetail]:
    modules = [
        {
            "id": "nongbo-login-auth",
            "title": "登录认证与用户信息",
            "summary": "对照真实 AuthController、SysUserService 和登录接口说明理解后台登录认证。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/AuthController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/ISysUserService.java",
                PROJECT_FRONTEND / "后端登录接口实现说明.md",
            ],
            "docs": [PROJECT_DOC_DIR / "04-接口规范.md"],
        },
        {
            "id": "nongbo-system-management",
            "title": "系统管理：用户、角色与配置",
            "summary": "围绕 SystemManagementController、sys_user、sys_role、sys_config 完成后台基础管理理解。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/SystemManagementController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/SysUser.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/SysRole.java",
            ],
            "docs": [PROJECT_DOC_DIR / "03-数据库规划.md", PROJECT_DOC_DIR / "04-接口规范.md"],
        },
        {
            "id": "nongbo-knowledge-management",
            "title": "知识管理：专家、图文课程与视频课程",
            "summary": "对照专家、图文课程、视频课程三个真实管理模块理解知识内容维护。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbExpertController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbGraphicCourseController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbVideoCourseController.java",
            ],
            "docs": [PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_DOC_DIR / "04-接口规范.md"],
        },
        {
            "id": "nongbo-policy-management",
            "title": "补贴政策管理",
            "summary": "基于 NbAllowancePolicyController 和 nb_allowance_policy 表理解政策发布、推荐与上下架。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbAllowancePolicyController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbAllowancePolicyServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbAllowancePolicy.java",
            ],
            "docs": [PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-loan-management",
            "title": "信贷信息管理",
            "summary": "基于 NbCreditLoanController 和 nb_credit_loan 表理解信贷产品维护。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbCreditLoanController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbCreditLoanServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbCreditLoan.java",
            ],
            "docs": [PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-service-management",
            "title": "农事服务管理",
            "summary": "基于 NbServiceController 和 nb_service 表理解农事服务信息维护。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbServiceController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbServiceServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbService.java",
            ],
            "docs": [PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-produce-management",
            "title": "农产品管理",
            "summary": "基于 NbFarmProduceController 和 nb_farm_produce 表理解农产品信息维护。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbFarmProduceController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbFarmProduceServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbFarmProduce.java",
            ],
            "docs": [PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-market-management",
            "title": "农贸市场与行情管理",
            "summary": "基于 NbFarmMarketController 和 nb_farm_market 表理解市场行情维护。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbFarmMarketController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbFarmMarketServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbFarmMarket.java",
            ],
            "docs": [PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-advertisement-management",
            "title": "广告管理",
            "summary": "基于 NbAdvertisementController 和 nb_advertisement 表理解广告位维护、发布与取消发布。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbAdvertisementController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbAdvertisementServiceImpl.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbAdvertisement.java",
            ],
            "docs": [PROJECT_ROOT / "nb_database.sql"],
        },
        {
            "id": "nongbo-file-upload",
            "title": "文件上传",
            "summary": "基于 FileUploadController 和 FileUploadConfig 理解后台图片/文件上传接口。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/FileUploadController.java",
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/config/FileUploadConfig.java",
            ],
            "docs": [PROJECT_DOC_DIR / "04-接口规范.md"],
        },
        {
            "id": "nongbo-data-statistics",
            "title": "数据统计",
            "summary": "基于 DataStatisticsController 理解后台统计接口与数据大屏支撑。",
            "files": [
                PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/DataStatisticsController.java",
                PROJECT_FRONTEND / "src/components/views/DataDashboard.vue",
            ],
            "docs": [PROJECT_DOC_DIR / "01-项目需求分析.md"],
        },
        {
            "id": "nongbo-frontend-integration",
            "title": "完整前后端联调",
            "summary": "基于 Vue 请求封装、Pinia、路由和真实接口前缀完成后台管理系统联调。",
            "files": [
                PROJECT_FRONTEND / "src/utils/request.ts",
                PROJECT_FRONTEND / "src/store/user-with-api.ts",
                PROJECT_FRONTEND / "src/router/router.ts",
                PROJECT_FRONTEND / "Pinia连接后端API说明.md",
            ],
            "docs": [PROJECT_ROOT / "项目5-完整前后端对接" / "README.md", PROJECT_DOC_DIR / "04-接口规范.md"],
        },
    ]
    route_modules = [module for module in modules if module["id"] != "nongbo-data-statistics"]
    return [_project_lesson(module) for module in route_modules]


def _build_nongbo_lessons() -> list[LessonDetail]:
    """Build the Nongbo route from the Web application course standard."""
    modules = [
        {
            "id": "nongbo-requirement-architecture",
            "title": "项目1：需求认知与分层架构",
            "summary": "按课程标准“Spring简介与Web结构”要求，从农宝需求、接口和源码目录理解 B/S、三层架构与请求链路。",
            "standard_unit": "项目1 Spring框架核心 - 1.1 Spring简介与Web结构",
            "objectives": ["描述农宝后台的 B/S 架构和三层职责", "串起 Vue、Controller、Service、数据库的一次请求链路", "定位真实源码中的 Controller、Service、Entity/Mapper 和配置文件"],
            "files": [PROJECT_ROOT / "项目1-需求与技术方案" / "01-项目需求分析.md", PROJECT_ROOT / "项目1-需求与技术方案" / "02-技术方案规划.md", PROJECT_ROOT / "项目5-完整前后端对接" / "README.md"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_DOC_DIR / "04-接口规范.md"],
            "practice_title": "梳理农宝后台的一次完整请求链路",
            "practice_description": "阅读课程标准项目1要求和农宝真实需求，补全从前端页面到后端接口、业务服务、数据库表的调用说明。",
            "checklist": ["说明 B/S 架构、前端 Vue 和后端 Spring Boot 的职责边界", "包含 Controller -> Service -> Entity/Mapper -> 数据库链路", "引用农宝需求或接口规范中的真实模块名称", "指出统一返回 Result<T> 或接口前缀等项目规范"],
        },
        {
            "id": "nongbo-ioc-di-layering",
            "title": "项目1：IoC/DI 与三层解耦",
            "summary": "按课程标准 IoC/DI、Bean 管理要求，借农宝真实 Controller 注入 Service 的写法理解解耦。",
            "standard_unit": "项目1 Spring框架核心 - 1.3 Spring IoC与依赖注入 / 1.4 Spring Bean管理",
            "objectives": ["解释 @Autowired 注入接口而不是手写 new 的解耦价值", "定位 Controller、Service 接口和实现类之间的依赖关系", "说明 Bean 扫描、作用域和生命周期对后台模块的影响"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbFarmProduceController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/INbFarmProduceService.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbFarmProduceServiceImpl.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "02-技术方案规划.md"],
            "practice_title": "补全农产品模块的依赖注入说明",
            "practice_description": "围绕农产品模块，说明 Controller 为什么依赖 Service 接口、ServiceImpl 如何承接业务、Entity/Mapper 如何隔离数据访问。",
            "checklist": ["包含 @Autowired 或构造注入的依赖注入说明", "说明 Controller 不直接访问 Mapper 的原因", "解释接口类型 INbFarmProduceService 的解耦作用", "说明该结构如何支撑后续自测和维护"],
        },
        {
            "id": "nongbo-aop-transaction-quality",
            "title": "项目2：AOP、事务与质量意识",
            "summary": "对照课程标准的 AOP 与事务管理要求，分析农宝业务中日志、事务和数据一致性应该落在哪里。",
            "standard_unit": "项目2 Spring AOP与事务管理",
            "objectives": ["解释 AOP 适合处理日志、性能监控、权限校验等横切关注点", "识别新增、上下架、删除等业务中需要事务保护的场景", "把质量意识落实为日志、异常和回滚策略"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbAllowancePolicyServiceImpl.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbAllowancePolicyController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/common/Result.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "03-数据库规划.md", ROOT_NONGBO_SQL],
            "practice_title": "给补贴政策模块设计事务和日志检查点",
            "practice_description": "不要生成完整项目，只补全或说明补贴政策发布、推荐、上下架时应如何记录日志、处理异常和保证数据一致性。",
            "checklist": ["说明 AOP 横切关注点，不把日志散落到每个业务分支", "指出至少一个需要 @Transactional 或回滚保护的业务动作", "保留 Result<T> 统一响应和异常提示", "依据 nb_allowance_policy 表字段说明状态变更"],
        },
        {
            "id": "nongbo-login-auth",
            "title": "项目3：登录认证 Controller",
            "summary": "按课程标准 Spring MVC Controller、参数接收和登录功能实验要求，对照 AuthController 完成认证链路学习。",
            "standard_unit": "项目3 Spring MVC Web开发 - 3.2 Controller开发进阶",
            "objectives": ["说明登录接口的请求路径、请求体、校验逻辑和返回结构", "解释 Controller 如何接收 JSON 参数并调用用户服务", "识别教学 Token 与生产 JWT/Session 方案的区别"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/AuthController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/ISysUserService.java", PROJECT_FRONTEND / "后端登录接口实现说明.md"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "04-接口规范.md"],
            "practice_title": "补全登录认证接口的关键校验",
            "practice_description": "基于 AuthController 和接口规范，只补全用户存在性、密码比对、Result 返回和 token 说明，不扩写成完整权限系统。",
            "checklist": ["接口路径沿用真实项目登录接口或 /dev-api/yjnb 前缀", "校验用户不存在和密码错误两类失败场景", "登录成功返回 Result<T> 和 token/用户信息", "说明教学 Token 与 JWT/Session 的差异"],
        },
        {
            "id": "nongbo-mvc-validation-exception",
            "title": "项目3：数据绑定、校验与异常处理",
            "summary": "承接课程标准的数据绑定、JSON交互、验证和全局异常处理要求，用系统管理模块理解健壮 API。",
            "standard_unit": "项目3 Spring MVC Web开发 - 3.3/3.5/3.7",
            "objectives": ["说明系统管理接口如何接收复杂对象和分页查询参数", "为用户、角色、配置维护设计必要的入参校验", "说明异常统一处理如何改善前后端联调体验"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/SystemManagementController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/SysUser.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/SysRole.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "03-数据库规划.md", PROJECT_DOC_DIR / "04-接口规范.md", ROOT_NONGBO_SQL],
            "practice_title": "为系统管理接口补一组校验与错误返回",
            "practice_description": "围绕用户、角色或配置维护，补充参数校验、Result 错误返回和异常处理说明。",
            "checklist": ["说明 @RequestBody、查询参数或路径参数的使用场景", "至少覆盖一个必填、长度或状态值校验", "错误响应仍使用 Result<T> 或项目统一结构", "字段名称对应 sys_user、sys_role 或 sys_config 表"],
        },
        {
            "id": "nongbo-file-upload",
            "title": "项目3：文件上传与资源接口",
            "summary": "按课程标准文件上传下载要求，对照 FileUploadController 理解图片/附件上传的接口边界。",
            "standard_unit": "项目3 Spring MVC Web开发 - 3.8 文件上传与下载",
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/FileUploadController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/config/FileUploadConfig.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "04-接口规范.md"],
            "practice_title": "补全上传接口的安全与返回说明",
            "practice_description": "结合真实上传 Controller 和配置，说明上传参数、保存路径、访问 URL、文件类型/大小限制与错误返回。",
            "checklist": ["使用 MultipartFile 或真实上传接口参数", "说明上传目录、访问 URL 或 FileUploadConfig 配置", "包含文件类型、大小或空文件校验", "上传结果使用统一 Result<T> 返回"],
        },
        {
            "id": "nongbo-database-crud-produce",
            "title": "项目4：MyBatis CRUD 与农产品表",
            "summary": "按课程标准 MyBatis 环境、SQL 映射和 CRUD 要求，围绕 nb_farm_produce 完成数据持久化学习。",
            "standard_unit": "项目4 MyBatis数据持久化与SSM整合 - 4.1",
            "objectives": ["从 nb_database.sql 定位农产品表结构和字段含义", "说明 Entity、Mapper、Service、Controller 的 CRUD 分工", "用真实字段补全新增、查询或更新的关键代码/说明"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbFarmProduceController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbFarmProduceServiceImpl.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbFarmProduce.java"],
            "docs": [COURSE_STANDARD_DOC, ROOT_NONGBO_SQL, PROJECT_DOC_DIR / "03-数据库规划.md"],
            "practice_title": "补全农产品 CRUD 的字段依据",
            "practice_description": "阅读表结构和真实代码，补全一个农产品新增/查询/更新片段或说明字段如何从请求映射到数据库。",
            "checklist": ["字段、表名或实体属性对应 nb_farm_produce", "说明 Controller -> Service -> Mapper/Entity 的调用顺序", "包含新增、查询、更新或删除中的至少一种 CRUD 逻辑", "不编造 SQL 字段，必须依据数据库或源码"],
        },
        {
            "id": "nongbo-dynamic-query-loan-market",
            "title": "项目4：动态查询、分页与行情信贷",
            "summary": "按课程标准动态 SQL、复杂查询和分页要求，分析信贷产品与市场行情的列表检索。",
            "standard_unit": "项目4 MyBatis数据持久化与SSM整合 - 4.2",
            "objectives": ["说明列表查询中的条件筛选、分页和排序依据", "对照信贷/行情表字段设计动态查询条件", "识别 PageQuery、统一响应或查询封装的作用"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbCreditLoanController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/service/impl/NbCreditLoanServiceImpl.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/entity/NbCreditLoan.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbFarmMarketController.java"],
            "docs": [COURSE_STANDARD_DOC, ROOT_NONGBO_SQL],
            "practice_title": "设计信贷或行情列表的动态查询条件",
            "practice_description": "选择信贷或市场行情模块，补全查询条件、分页参数和返回结构说明，体现动态 SQL/查询封装思想。",
            "checklist": ["查询字段来自 nb_credit_loan 或 nb_farm_market 表", "包含分页、关键词、状态或分类中的至少两类条件", "说明空条件时不能拼出错误 SQL 或错误查询", "返回结构遵循真实项目统一响应"],
        },
        {
            "id": "nongbo-knowledge-management",
            "title": "项目4：综合模块协作与知识内容管理",
            "summary": "按课程标准综合实战要求，把专家、图文课程、视频课程作为一个内容管理子系统进行协作分析。",
            "standard_unit": "项目4 MyBatis数据持久化与SSM整合 - 4.3 综合实战",
            "objectives": ["把专家、图文课程、视频课程归纳为内容管理业务域", "说明多个模块共用的分页、状态、排序和图片字段处理方式", "从需求、接口、数据库、源码四类依据完成实现复盘"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbExpertController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbGraphicCourseController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbVideoCourseController.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "01-项目需求分析.md", PROJECT_DOC_DIR / "04-接口规范.md", ROOT_NONGBO_SQL],
            "practice_title": "复盘知识内容管理子系统的共性实现",
            "practice_description": "从专家、图文课程、视频课程中任选两个模块，比较它们的接口、字段、服务调用和验收点。",
            "checklist": ["至少比较两个真实 Controller 或实体", "说明共用的分页、状态、图片或排序处理", "引用需求、接口规范、数据库或源码中的真实依据", "提出一个可复用的 Service/校验/返回结构改进点"],
        },
        {
            "id": "nongbo-springboot-config-mybatisplus",
            "title": "项目5：Spring Boot 配置与 MyBatis-Plus",
            "summary": "按课程标准 Spring Boot 核心、自动配置和 MyBatis-Plus 整合要求，理解农宝后台快速开发结构。",
            "standard_unit": "项目5 Spring Boot进阶与现代化开发 - 5.1/5.2",
            "objectives": ["说明 Spring Boot 项目结构、配置文件和自动配置的作用", "识别 MyBatis-Plus/BaseMapper 或通用 Service 简化 CRUD 的价值", "根据项目上下文判断全局、数据库或上传配置"],
            "files": [PROJECT_BACKEND / "src/main/resources/application.yml", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/NbspringproductApplication.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/mapper/NbFarmProduceMapper.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "02-技术方案规划.md", ROOT_NONGBO_SQL],
            "practice_title": "说明农宝项目的 Spring Boot 自动配置落点",
            "practice_description": "围绕启动类、application.yml、Mapper/Service 结构，补全项目如何通过 Spring Boot 和 MyBatis-Plus 简化开发。",
            "checklist": ["提到启动类、配置文件或自动配置机制", "说明数据库连接、上传路径或跨域配置中的至少一类配置", "说明 MyBatis-Plus/Mapper 如何简化 CRUD", "结合农宝真实源码路径，不泛泛谈概念"],
        },
        {
            "id": "nongbo-business-service-policy",
            "title": "项目5：业务模块扩展与政策服务",
            "summary": "按照课程标准“学生展示综合设计项目成果”的要求，把补贴政策、农事服务、广告管理作为 Spring Boot 业务扩展任务。",
            "standard_unit": "项目5 Spring Boot进阶与现代化开发 - 综合设计展示",
            "objectives": ["抽取一个可复用的业务模块开发流程", "说明需求、建表、Entity、Service、Controller、接口测试的顺序", "用政策/农事服务/广告中的真实字段完成模块扩展复盘"],
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbAllowancePolicyController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbServiceController.java", PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/NbAdvertisementController.java"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "01-项目需求分析.md", ROOT_NONGBO_SQL],
            "practice_title": "按企业流程复盘一个业务模块扩展",
            "practice_description": "从补贴政策、农事服务、广告管理中任选一个模块，按需求、表结构、实体、服务、接口、自测顺序写出实现依据。",
            "checklist": ["开发顺序包含需求 -> 建表 -> Entity -> Service -> Controller -> 测试", "字段或状态来自真实 SQL/源码", "说明接口自测方式和至少一个失败场景", "不鼓励生成完整项目，只补关键代码或依据说明"],
        },
        {
            "id": "nongbo-data-statistics",
            "title": "项目5：数据统计与成果展示",
            "summary": "结合课程标准的综合设计展示要求，对照 DataStatisticsController 和数据大屏完成项目成果汇报。",
            "standard_unit": "项目5 Spring Boot进阶与现代化开发 - 学生展示综合设计项目成果",
            "files": [PROJECT_BACKEND / "src/main/java/com/movie/nbspringproduct/controller/DataStatisticsController.java", PROJECT_FRONTEND / "src/components/views/DataDashboard.vue"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_DOC_DIR / "01-项目需求分析.md", ROOT_NONGBO_SQL],
            "practice_title": "准备农宝后台成果展示的数据依据",
            "practice_description": "围绕统计接口和数据大屏，说明统计指标从哪些表来、接口如何返回、展示时如何证明功能真实可用。",
            "checklist": ["至少说明两个统计指标及其数据来源", "包含 DataStatisticsController 或数据大屏组件依据", "说明接口返回结构和前端展示字段的对应关系", "体现作品验收、设计报告或答辩所需证据"],
        },
        {
            "id": "nongbo-frontend-integration",
            "title": "项目5：Vue 前后端联调与复盘",
            "summary": "按课程标准过程驱动与综合项目展示要求，完成农宝 Vue 请求封装、Pinia、路由和真实接口联调复盘。",
            "standard_unit": "项目5 Spring Boot进阶与现代化开发 - 综合设计展示与过程评价",
            "objectives": ["说明 Vue 请求封装如何对接后端 /dev-api/yjnb 前缀", "解释登录状态、路由守卫或 Pinia 状态与后端接口的关系", "按读需求、找依据、补代码、自测、复盘完成完整学习闭环"],
            "files": [PROJECT_FRONTEND / "src/utils/request.ts", PROJECT_FRONTEND / "src/store/user-with-api.ts", PROJECT_FRONTEND / "src/router/router.ts", PROJECT_FRONTEND / "Pinia连接后端API说明.md"],
            "docs": [COURSE_STANDARD_DOC, PROJECT_ROOT / "项目5-完整前后端对接" / "README.md", PROJECT_DOC_DIR / "04-接口规范.md"],
            "practice_title": "完成一次真实接口联调复盘",
            "practice_description": "选择登录、列表或上传中的一个流程，说明前端请求、后端接口、状态管理、自测结果和复盘改进。",
            "checklist": ["包含 Vue 请求封装或 Pinia/路由中的真实文件依据", "接口前缀、路径和后端 Controller 能对应上", "说明自测方法、成功结果和至少一个失败排查点", "复盘中只给提示和检查，不生成完整项目"],
        },
    ]
    route_modules = [module for module in modules if module["id"] != "nongbo-data-statistics"]
    return [_project_lesson(module) for module in route_modules]


def _project_lesson(module: dict) -> LessonDetail:
    files = [path for path in module["files"] if path.exists()]
    docs = [path for path in module.get("docs", []) if path.exists()]
    code_path = files[0] if files else None
    code = _read_text(code_path) if code_path else ""
    doc_excerpt = "\n\n".join(_plain_excerpt(_read_knowledge_text(path), 600) for path in docs)
    source_list = "\n".join(f"- {_rel(path)}" for path in [*files, *docs])
    template = _project_template(code, code_path)
    standard_unit = module.get("standard_unit", "")
    objectives = module.get("objectives") or [
        "定位真实 Controller、Service、Entity/Mapper 和接口路径",
        "说明 Result<T> 统一返回结构和 /dev-api/yjnb 前端接口前缀",
        "对照数据库字段或需求规格完成实现依据说明",
    ]
    checklist = module.get("checklist") or [
        "接口路径沿用真实项目前缀 /dev-api/yjnb 或现有控制器路径",
        "返回结构使用 com.movie.nbspringproduct.common.Result<T>",
        "Service 命名和调用沿用 IxxxService / xxxService",
        "字段、表名或页面名称能对应真实需求、数据库或源码",
    ]
    return LessonDetail(
        id=module["id"],
        course_id=NONGBO_COURSE_ID,
        title=module["title"],
        summary=module["summary"],
        objectives=objectives,
        content="\n\n".join(
            part
            for part in [
                f"课程标准对应：{standard_unit}" if standard_unit else "",
                f"资料来源：\n{source_list}",
                f"项目文档摘录：\n{doc_excerpt}" if doc_excerpt else "",
                f"关键代码摘录：\n```java\n{template}\n```" if template else "",
            ]
            if part
        ),
        practice=PracticeTask(
            title=module.get("practice_title") or f"{module['title']}真实项目实现复盘",
            description=module.get("practice_description") or "阅读真实项目代码和文档，补全或说明该模块的接口、服务调用、实体字段和返回结构。",
            template=template or "当前模块没有可摘录的代码文件，请粘贴真实项目相关代码或接口说明。",
            checklist=checklist,
        ),
        source=_rel(code_path) if code_path else None,
    )


def _project_template(code: str, path: Path | None) -> str:
    if not code.strip():
        return ""
    if path and path.suffix == ".vue":
        return _plain_excerpt(code, 1400)
    if path and path.suffix == ".java":
        return _plain_excerpt(code, 1800)
    class_match = re.search(r"((?:@RestController|public class|export default|const ).{0,4000})", code, re.S)
    snippet = class_match.group(1) if class_match else code
    return _plain_excerpt(snippet, 1600)


def _springboot_practice_template(content: str, code_index: str) -> str:
    blocks = _extract_code_blocks(content)
    if blocks:
        return "\n\n".join(blocks[:3])
    if code_index.strip():
        return (
            "// 本讲资料只提供了配套代码索引，未抽取到完整代码块。\n"
            "// 请根据下方真实文件路径打开对应源码，再粘贴你的实现或命令输出。\n\n"
            f"{code_index}"
        )
    return "本讲资料未提供固定代码模板，请粘贴课堂代码、配置或构建命令结果。"


def _extract_code_blocks(content: str) -> list[str]:
    blocks: list[str] = []
    for match in re.finditer(r"```(?P<lang>[a-zA-Z0-9_-]*)\n(?P<code>[\s\S]*?)```", content):
        code = match.group("code").strip()
        if len(code) < 80:
            continue
        if code.startswith("Slide "):
            continue
        lang = match.group("lang").strip()
        header = f"// 代码类型: {lang}\n" if lang and lang not in {"text", "txt"} else ""
        blocks.append(_plain_excerpt(f"{header}{code}", 1800))
    return blocks


def _read_text(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _read_knowledge_text(path: Path | None) -> str:
    if path is None:
        return ""
    if path.suffix.lower() == ".doc":
        return _read_legacy_doc_text(path)
    return _read_text(path)


def _read_legacy_doc_text(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    text = data.decode("utf-16le", errors="ignore")
    runs = re.findall(r"[\u4e00-\u9fffA-Za-z0-9（）()《》、，。；：:/.\\\-\s]{8,}", text)
    cleaned = []
    for run in runs:
        compact = " ".join(run.split())
        if compact and any("\u4e00" <= char <= "\u9fff" for char in compact):
            cleaned.append(compact)
    return "\n\n".join(cleaned)


def _first_heading(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return ""


def _extract_section(content: str, marker: str, max_chars: int) -> str:
    start = content.find(marker)
    if start < 0:
        return ""
    next_heading = content.find("\n## ", start + len(marker))
    section = content[start: next_heading if next_heading > start else len(content)]
    return _plain_excerpt(section, max_chars)


def _extract_bullets(content: str, marker: str) -> list[str]:
    section = _extract_section(content, marker, 1400)
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items[:8]


def _plain_excerpt(content: str, limit: int) -> str:
    compact = content.strip()
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def _rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
