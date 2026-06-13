from __future__ import annotations

from backend.app.data.courses import NONGBO_COURSE_ID, SPRINGBOOT_COURSE_ID, get_lessons


NONGBO_RUNTIME_SEED = {
    "courseLine": {
        "slug": NONGBO_COURSE_ID,
        "title": "农宝系统后台管理项目实训",
        "description": "基于农宝系统真实需求、数据库、接口文档和源码，引导学生完成 Spring Boot 后端模块开发。",
        "targetAudience": "软件技术专业 Web 应用系统开发课程学生",
        "techStack": ["Spring Boot", "MyBatis-Plus", "MySQL", "RESTful API", "Vue 3"],
        "status": "active",
    },
    "modules": [
        {
            "slug": "nongbo-lecture-course-management",
            "title": "农科讲堂课程管理模块",
            "description": "围绕农科讲堂课程内容管理，完成从需求理解到接口联调的闯关训练。",
            "businessContext": "农科讲堂需要展示推荐课程、课程详情、专家关联、搜索与学习观看，后台需要提供可维护的数据与接口。",
            "tasks": [
                {
                    "slug": "task-requirement-understanding",
                    "title": "需求理解",
                    "type": "analysis",
                    "goal": "说明农科讲堂课程管理模块至少要支撑哪些业务功能。",
                    "scenario": "你正在接手农宝后台的农科讲堂课程管理，需要先读懂前后台业务边界。",
                    "instruction": "请用自己的话说明课程管理模块的核心功能，不要直接写代码。",
                    "requiredArtifactType": "text",
                    "difficulty": 1,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "concept",
                            "name": "功能识别",
                            "weight": 40,
                            "required": True,
                            "config": {
                                "concepts": ["课程列表", "课程详情", "搜索", "推荐课程", "专家关联", "在线学习", "观看"],
                                "minHit": 4,
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
                            "name": "防止直接抄答案",
                            "weight": 30,
                            "required": False,
                            "config": {"forbiddenPatterns": ["完整项目", "所有文件", "一键生成", "直接给我代码"]},
                        },
                    ],
                },
                {
                    "slug": "task-course-table-design",
                    "title": "数据库设计",
                    "type": "database_design",
                    "goal": "设计课程表字段，支撑列表、详情、搜索、推荐、排序和专家关联。",
                    "scenario": "后台需要维护农科讲堂课程，前台需要展示课程卡片和课程详情。",
                    "instruction": "请设计课程表字段并说明用途，暂时不需要写完整建表 SQL。",
                    "requiredArtifactType": "field_list",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "核心字段",
                            "weight": 40,
                            "required": True,
                            "config": {
                                "keywords": ["id", "title", "content", "cover", "expert", "category", "view_count", "create_time"],
                                "minHit": 6,
                            },
                        },
                        {
                            "type": "concept",
                            "name": "业务支撑能力",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["专家关联", "课程列表", "课程详情", "搜索", "浏览量排序"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "资料贴合",
                            "weight": 25,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-entity-design",
                    "title": "实体类开发",
                    "type": "coding",
                    "goal": "根据数据库字段设计课程实体类，体现 MyBatis-Plus 风格。",
                    "scenario": "后端需要实体类承接课程表字段，并保持与项目包结构和命名习惯一致。",
                    "instruction": "请提交实体类关键字段、注解和说明，不要提交完整项目。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 75, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "实体结构",
                            "weight": 45,
                            "required": True,
                            "config": {"keywords": ["class", "private", "Long", "String", "LocalDateTime", "@Table", "id"], "minHit": 5},
                        },
                        {
                            "type": "concept",
                            "name": "字段映射理解",
                            "weight": 35,
                            "required": True,
                            "config": {"concepts": ["实体类", "数据库字段", "主键", "时间字段", "MyBatis-Plus"], "minHit": 3},
                        },
                        {
                            "type": "anti_shortcut",
                            "name": "提交边界",
                            "weight": 20,
                            "required": False,
                            "config": {"forbiddenPatterns": ["完整项目", "controller service mapper 全部", "所有代码"]},
                        },
                    ],
                },
                {
                    "slug": "task-mapper-service-controller",
                    "title": "Mapper/Service/Controller 开发",
                    "type": "coding",
                    "goal": "说明并提交课程管理模块三层调用关键片段。",
                    "scenario": "课程管理接口需要查询列表、详情、新增和修改，后端分层要清晰。",
                    "instruction": "请分别提交 Mapper、Service、Controller 的关键职责和核心片段。",
                    "requiredArtifactType": "java_snippet",
                    "difficulty": 3,
                    "unlockPolicy": {"minScore": 78, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "三层结构",
                            "weight": 40,
                            "required": True,
                            "config": {"keywords": ["Mapper", "Service", "Controller", "@RestController", "@RequestMapping", "Result"], "minHit": 5},
                        },
                        {
                            "type": "concept",
                            "name": "职责边界",
                            "weight": 40,
                            "required": True,
                            "config": {"concepts": ["Controller 接收请求", "Service 处理业务", "Mapper 访问数据库", "统一返回"], "minHit": 3},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "项目风格依据",
                            "weight": 20,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
                {
                    "slug": "task-api-test-reflection",
                    "title": "接口测试与学习总结",
                    "type": "reflection",
                    "goal": "说明接口测试路径、请求参数、返回结构和本次学习收获。",
                    "scenario": "完成模块开发后，需要证明接口可测，并复盘需求、数据库、分层代码之间的对应关系。",
                    "instruction": "请提交接口测试说明和学习总结，说明至少一个需要继续改进的问题。",
                    "requiredArtifactType": "reflection",
                    "difficulty": 2,
                    "unlockPolicy": {"minScore": 70, "requireCriticalCriteria": True},
                    "rubrics": [
                        {
                            "type": "keyword",
                            "name": "测试说明",
                            "weight": 35,
                            "required": True,
                            "config": {"keywords": ["GET", "POST", "路径", "参数", "返回", "Result", "测试"], "minHit": 4},
                        },
                        {
                            "type": "concept",
                            "name": "复盘质量",
                            "weight": 45,
                            "required": True,
                            "config": {"concepts": ["需求", "数据库", "实体", "接口", "改进", "问题"], "minHit": 4},
                        },
                        {
                            "type": "rag_grounded",
                            "name": "证据支撑",
                            "weight": 20,
                            "required": False,
                            "config": {"minEvidence": 1},
                        },
                    ],
                },
            ],
        }
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
