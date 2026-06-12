import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PPT_ROOT = ROOT / "ppt"
OUT = ROOT / "docs" / "course-materials"


def ppt_slides(ppt: Path) -> list[tuple[int, str]]:
    slides: list[tuple[int, str]] = []
    with zipfile.ZipFile(ppt) as archive:
        names = sorted(
            [
                name
                for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ],
            key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),
        )
        for index, name in enumerate(names, 1):
            tree = ET.fromstring(archive.read(name))
            texts: list[str] = []
            for elem in tree.iter():
                if elem.tag.endswith("}t") and elem.text:
                    text = " ".join(elem.text.split())
                    if text:
                        texts.append(text)
            compact: list[str] = []
            for text in texts:
                if not compact or compact[-1] != text:
                    compact.append(text)
            if compact:
                slides.append((index, " ".join(compact)))
    return slides


def code_files(base: Path) -> list[tuple[str, list[str]]]:
    refs: list[tuple[str, list[str]]] = []
    for child in base.iterdir():
        if not child.is_dir() or child.name == "PPT":
            continue
        for file in sorted(child.rglob("*")):
            if not file.is_file():
                continue
            if any(part in {"target", ".idea", ".mvn"} for part in file.parts):
                continue
            if file.suffix.lower() not in {
                ".java",
                ".xml",
                ".properties",
                ".yml",
                ".yaml",
                ".sql",
                ".html",
                ".js",
                ".css",
            }:
                continue
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            signals: list[str] = []
            for line in [line.strip() for line in content.splitlines() if line.strip()]:
                lowered = line.lower()
                if any(
                    key in lowered
                    for key in [
                        "@restcontroller",
                        "@service",
                        "@mapper",
                        "@springbootapplication",
                        "@aspect",
                        "@bean",
                        "@configuration",
                        "@interceptor",
                        "@webfilter",
                        "class ",
                        "interface ",
                        "select ",
                        "insert ",
                        "update ",
                        "delete ",
                        "create table",
                        "<dependency",
                        "server.port",
                        "spring.datasource",
                    ]
                ):
                    signals.append(line)
                if len(signals) >= 5:
                    break
            refs.append((str(file.relative_to(ROOT)), signals))
    return refs


META = [
    {
        "slug": "03-maven-basic",
        "prefix": "03.",
        "title": "Maven 基础与 Java 项目构建",
        "summary": "让学生理解 Maven 的项目结构、依赖坐标、生命周期和测试打包流程，为后续 SpringBoot 工程做准备。",
        "thesis": "Maven 不是背命令，而是用统一结构和生命周期把 Java 项目的构建、依赖、测试、打包变成可复现流程。",
        "objectives": [
            "解释 Maven 的作用：项目构建、统一结构、依赖管理",
            "读懂 pom.xml 中 groupId、artifactId、version、dependency",
            "能使用 compile、test、package 完成基础构建",
            "能说明本地仓库、中央仓库、依赖传递的关系",
        ],
        "concepts": ["Maven 的工程价值", "标准目录结构", "依赖坐标与仓库", "生命周期与插件"],
        "demos": [
            "展示普通 Java 项目到 Maven 项目的目录变化",
            "修改 pom.xml 增加 commons-io 或 JUnit 依赖",
            "运行测试并打包 jar，观察 target 目录变化",
        ],
        "practice": [
            "补全一个 Maven 项目的 pom.xml，添加 JUnit 依赖并编写一个 Service 单元测试。",
            "学生需提交 pom.xml、测试类和 mvn test/package 的结果说明。",
        ],
        "pitfalls": [
            "把 Maven 当成 IDE 插件，只会点按钮不会解释生命周期",
            "依赖版本写错或 scope 理解错误",
            "源码目录、测试目录放错导致编译失败",
        ],
    },
    {
        "slug": "04-springboot-web-basic",
        "prefix": "04.",
        "title": "SpringBoot Web 入门与分层解耦",
        "summary": "从 HTTP 请求处理、Controller 入门、三层架构到 IOC/DI，建立 SpringBoot Web 开发第一条完整调用链。",
        "thesis": "SpringBoot Web 教学的核心不是跑通 /hello，而是让学生看见请求如何进入 Controller，并逐步拆分到 Service/Dao。",
        "objectives": [
            "能创建 SpringBoot Web 工程并暴露 GET 接口",
            "能区分静态资源、动态资源和 B/S 架构",
            "能描述 Controller、Service、Dao 的职责",
            "理解 IOC/DI 如何降低层间耦合",
        ],
        "concepts": ["SpringBoot 快速开发", "HTTP 请求处理", "三层架构", "IOC 与 DI"],
        "demos": [
            "完成 /hello?name=xxx 接口",
            "演示用户列表从 Controller 到 Service 到 Dao 的拆分",
            "把 new 对象改为 @Service + 构造器注入",
        ],
        "practice": [
            "基于资料中的用户列表案例，重构为 Controller-Service-Dao 三层，并说明每层职责。",
            "提交接口路径、关键代码和一次请求的调用链说明。",
        ],
        "pitfalls": [
            "把所有逻辑写在 Controller",
            "不会解释 @Component、@Service、构造器注入差异",
            "返回格式不稳定，前端难以联调",
        ],
    },
    {
        "slug": "05-mysql-sql",
        "prefix": "05.",
        "title": "MySQL 数据库与 SQL 基础",
        "summary": "讲授数据库、DBMS、SQL、表结构、约束、多表设计、查询和事务，为 Web 后端持久化建立基础。",
        "thesis": "数据库课要把“会写 SQL”升级为“会用表结构表达业务关系，并保证数据一致性”。",
        "objectives": [
            "理解数据库、DBMS、SQL 的关系",
            "掌握 DDL、DML、DQL、DCL 的基本使用",
            "能设计带主键、唯一约束、外键的基础表结构",
            "能解释事务 ACID 和提交/回滚",
        ],
        "concepts": ["数据库与 DBMS", "SQL 分类", "表结构与约束", "事务与一致性"],
        "demos": [
            "创建 dept/emp 等业务表",
            "演示 insert、update、delete、select",
            "演示多表查询与事务失败回滚",
        ],
        "practice": [
            "设计 Tlias 部门与员工表，并编写部门列表、员工查询、删除部门前校验的 SQL。",
            "提交建表 SQL、查询 SQL 和一致性说明。",
        ],
        "pitfalls": ["只会写单表查询，不会从业务关系推导表结构", "误删有关联数据导致不一致", "混淆事务和普通 SQL 执行顺序"],
    },
    {
        "slug": "06-jdbc-mybatis",
        "prefix": "06.",
        "title": "JDBC、连接池与 MyBatis 入门",
        "summary": "从 JDBC 规范和 PreparedStatement 出发，引出连接池、MyBatis Mapper、XML/注解 SQL 与 SpringBoot 整合。",
        "thesis": "让学生先感受 JDBC 的重复代码，再理解 MyBatis 为什么能把 SQL 与对象映射组织起来。",
        "objectives": [
            "理解 JDBC 是 Java 操作关系型数据库的 API 规范",
            "能使用 PreparedStatement 防止 SQL 注入",
            "了解连接池降低连接创建成本",
            "能编写 Mapper 接口完成基础 CRUD",
        ],
        "concepts": ["JDBC 规范与驱动", "PreparedStatement", "数据库连接池", "MyBatis Mapper"],
        "demos": [
            "用 JDBC 执行 update/select 并封装 User",
            "把硬编码 SQL 改为 PreparedStatement",
            "创建 MyBatis Mapper 并在 SpringBoot 中测试查询",
        ],
        "practice": [
            "将 JDBC 登录查询改造成 MyBatis Mapper，并说明 SQL 注入防护点。",
            "提交 Mapper 接口、SQL 映射和测试入口。",
        ],
        "pitfalls": ["资源未关闭导致连接泄露", "字符串拼接 SQL", "字段名与对象属性映射不清晰"],
    },
    {
        "slug": "07-dept-management",
        "prefix": "07.",
        "title": "Tlias 部门管理与 RESTful 接口",
        "summary": "围绕部门查询、新增、修改、删除实现前后端分离接口，建立统一响应、日志和接口文档意识。",
        "thesis": "部门管理是第一个完整 CRUD 实战，重点是按接口契约开发，而不是后端单方面“能跑就行”。",
        "objectives": [
            "能按 RESTful 风格设计部门资源接口",
            "能实现 Result 统一响应结构",
            "能完成部门 CRUD 的 Controller-Service-Mapper 调用链",
            "能使用日志定位请求参数与执行结果",
        ],
        "concepts": ["前后端分离开发流程", "RESTful 风格", "统一响应 Result", "部门 CRUD 调用链"],
        "demos": [
            "搭建 tlias-web-management 工程",
            "实现 GET /depts 查询部门",
            "实现 POST、PUT、DELETE 并联调前端请求",
        ],
        "practice": [
            "完成部门管理 CRUD，并为每个接口写出请求方式、路径、参数、响应示例。",
            "提交接口说明与关键代码。",
        ],
        "pitfalls": ["接口路径和 HTTP 方法混乱", "返回值不统一", "Service 层缺失，Controller 直接访问 Mapper"],
    },
    {
        "slug": "08-emp-query",
        "prefix": "08.",
        "title": "员工管理一：多表关系、多表查询与分页",
        "summary": "讲授一对多、一对一、多对多关系、外键、连接查询，并完成员工列表分页和条件查询。",
        "thesis": "员工列表不是简单 select，而是多表关系、动态条件和分页结果结构的综合训练。",
        "objectives": [
            "能识别部门-员工的一对多关系",
            "理解外键约束与级联风险",
            "能编写员工条件分页查询",
            "能返回 records、total、page、pageSize 等分页结果",
        ],
        "concepts": ["多表关系", "外键约束", "连接查询", "分页与动态条件"],
        "demos": [
            "创建 dept、emp、emp_expr 等表关系",
            "演示 inner join、left join",
            "使用 PageHelper 或 limit 完成员工分页",
        ],
        "practice": [
            "实现员工列表条件分页：姓名、性别、入职时间范围、部门。",
            "提交 SQL/Mapper、返回结构和边界条件说明。",
        ],
        "pitfalls": ["连接查询字段冲突或别名缺失", "分页 total 与 records 不一致", "动态 SQL 空条件拼接错误"],
    },
    {
        "slug": "09-emp-save-upload-transaction",
        "prefix": "09.",
        "title": "员工管理二：新增员工、事务与文件上传",
        "summary": "围绕员工基本信息和工作经历批量保存，讲解主键回填、foreach 批量插入、声明式事务和文件上传。",
        "thesis": "一个员工新增操作可能写多张表，事务边界必须覆盖完整业务动作。",
        "objectives": [
            "能使用 @Options 获取自增主键",
            "能用 foreach 批量保存工作经历",
            "能解释 @Transactional 的回滚条件",
            "了解 MultipartFile 与对象存储/本地存储的边界",
        ],
        "concepts": ["新增员工业务链", "主键回填", "foreach 批量插入", "声明式事务与文件上传"],
        "demos": [
            "新增员工基本信息后回填 id",
            "批量插入 emp_expr",
            "故意制造异常观察事务回滚",
            "演示头像上传接口返回访问地址",
        ],
        "practice": [
            "实现新增员工接口：保存 emp 与 emp_expr，失败时整体回滚。",
            "提交 Service 方法、Mapper 批量 SQL 和一次失败回滚说明。",
        ],
        "pitfalls": ["事务加在 Controller 或 private 方法上无效", "只保存主表不保存子表", "上传文件名冲突或未限制类型"],
    },
    {
        "slug": "10-emp-update-exception-report",
        "prefix": "10.",
        "title": "员工管理三：删除、修改、异常处理与统计",
        "summary": "完成批量删除、查询回显、员工修改、全局异常处理和统计报表接口，把 CRUD 推向可维护状态。",
        "thesis": "成熟的 CRUD 不只是增删改查，还包括批量操作、异常可解释和统计结果可视化。",
        "objectives": [
            "能实现批量删除并清理关联工作经历",
            "能完成修改前查询回显与提交更新",
            "能使用 @RestControllerAdvice 统一异常响应",
            "能编写员工性别/职位统计接口",
        ],
        "concepts": ["批量删除", "查询回显与修改", "全局异常处理", "统计报表接口"],
        "demos": [
            "DELETE /emps?ids=1,2,3",
            "GET /emps/{id} 查询回显",
            "PUT /emps 修改员工",
            "统计员工职位分布并返回图表数据",
        ],
        "practice": [
            "补全员工批量删除和全局异常处理，要求删除 emp 与 emp_expr 一致。",
            "提交接口代码和异常响应示例。",
        ],
        "pitfalls": ["数组/集合参数绑定失败", "关联数据未删除", "异常信息直接暴露堆栈"],
    },
    {
        "slug": "11-project-practice",
        "prefix": "11.",
        "title": "班级与学员管理综合实战",
        "summary": "以小组形式完成班级管理、学员管理、违纪处理和统计报表，训练需求分析、接口实现、联调和演示表达。",
        "thesis": "项目实战的关键成果不是“照着写完”，而是能讲清实现思路、典型 Bug 和解决方案。",
        "objectives": [
            "能根据接口文档拆分班级/学员功能",
            "能完成 CRUD、违纪处理和统计接口",
            "能进行前后端联调与演示",
            "能复盘 Bug 原因和修复路径",
        ],
        "concepts": ["需求拆解", "接口清单", "前后端联调", "小组演示复盘"],
        "demos": [
            "小组拆分班级管理和学员管理任务",
            "按接口文档开发并联调",
            "准备演示脚本：功能、代码、Bug、改进",
        ],
        "practice": [
            "完成班级列表、新增、修改、删除与学员违纪处理，形成小组演示材料。",
            "提交接口清单、核心实现和复盘记录。",
        ],
        "pitfalls": ["只做功能不写接口说明", "联调时状态码和字段名不一致", "无法复盘问题，只说“改好了”"],
    },
    {
        "slug": "12-login-auth",
        "prefix": "12.",
        "title": "登录认证、会话技术、JWT 与拦截器",
        "summary": "从用户名密码登录引出登录标记、Cookie/Session、JWT、Filter/Interceptor 和统一登录校验。",
        "thesis": "登录认证要让学生理解“登录成功后如何在后续请求中证明身份”。",
        "objectives": [
            "能实现用户名密码登录查询",
            "理解 Cookie、Session、JWT 的差异",
            "能使用拦截器统一校验登录状态",
            "能说明 Token 过期、篡改和敏感信息风险",
        ],
        "concepts": ["登录功能本质", "会话技术", "JWT", "Filter 与 Interceptor"],
        "demos": [
            "POST /login 返回 token",
            "前端携带 token 请求部门/员工接口",
            "编写 LoginCheckInterceptor 放行登录接口并拦截其他接口",
            "演示未登录访问被拒绝",
        ],
        "practice": [
            "为 Tlias 系统补全登录认证：登录返回 JWT，其他接口通过拦截器校验。",
            "提交登录接口、JWT 工具、拦截器配置和失败响应。",
        ],
        "pitfalls": ["把密码明文写日志", "忘记放行登录接口", "JWT 密钥硬编码或过期时间缺失"],
    },
    {
        "slug": "13-aop-log",
        "prefix": "13.",
        "title": "AOP 与操作日志",
        "summary": "讲授连接点、切入点、通知、切面、目标对象和代理执行流程，并用自定义注解完成操作日志记录。",
        "thesis": "AOP 的教学重点是横切逻辑如何无侵入地织入业务方法。",
        "objectives": [
            "理解 AOP 五个核心概念",
            "能编写 @Aspect + @Around 统计耗时",
            "能用切入点表达式匹配业务方法",
            "能设计自定义注解记录操作日志",
        ],
        "concepts": ["AOP 适用场景", "连接点与切入点", "通知与切面", "操作日志案例"],
        "demos": [
            "引入 spring-boot-starter-aop",
            "编写 TimeAspect 统计业务层耗时",
            "用 @LogOperation 标记增删改方法",
            "记录请求人、方法名、参数、结果和耗时",
        ],
        "practice": [
            "实现一个操作日志切面：标注 @LogOperation 的方法执行后记录操作人、方法、参数、耗时和结果。",
            "提交注解、切面类和日志示例。",
        ],
        "pitfalls": ["切入点范围过大导致无关方法被拦截", "环绕通知忘记 proceed", "日志记录敏感参数"],
    },
    {
        "slug": "14-springboot-principle",
        "prefix": "14.",
        "title": "SpringBoot 原理、配置优先级、Bean 管理与 Maven 高级",
        "summary": "收束 SpringBoot 工作原理，讲解配置优先级、Bean 作用域、第三方 Bean、自定义 starter、自动配置、多模块、继承聚合和私服。",
        "thesis": "进阶课把“会用 SpringBoot”推进到“知道 starter、配置和模块化为什么这样工作”。",
        "objectives": [
            "能说明 SpringBoot 配置优先级",
            "理解 Bean 作用域和第三方 Bean 注册",
            "能解释自动配置和自定义 starter 的基本结构",
            "能进行 Maven 分模块、继承和聚合设计",
        ],
        "concepts": ["配置优先级", "Bean 作用域与第三方 Bean", "自动配置与 starter", "Maven 分模块、继承与聚合"],
        "demos": [
            "演示不同方式设置 server.port 的优先级",
            "注册第三方 Bean 到 Spring 容器",
            "拆分 tlias-pojo、tlias-utils、tlias-web-management",
            "分析自定义 aliyun-oss starter 的自动配置类",
        ],
        "practice": [
            "把单体 Tlias 工程拆成 pojo、utils、web-management 三个 Maven 模块，并说明依赖方向。",
            "提交模块结构、父 pom、子模块 pom 和依赖说明。",
        ],
        "pitfalls": ["配置文件格式混用导致覆盖困惑", "Bean 作用域误用", "子模块版本不统一或循环依赖"],
    },
]


def find_base(prefix: str) -> Path:
    matches = sorted(path for path in PPT_ROOT.iterdir() if path.is_dir() and path.name.startswith(prefix))
    if not matches:
        raise FileNotFoundError(f"No PPT directory with prefix {prefix}")
    return matches[0]


def write_materials() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lessons = []
    for order, meta in enumerate(META, 1):
        base = find_base(meta["prefix"])
        ppts = [ppt for ppt in sorted((base / "PPT").glob("*.pptx")) if not ppt.name.startswith("~$")]
        slide_sources: list[str] = []
        slide_lines: list[tuple[int, str]] = []
        for ppt in ppts:
            slides = ppt_slides(ppt)
            slide_sources.append(f"{ppt.relative_to(ROOT)}（{len(slides)} 页）")
            picked: list[tuple[int, str]] = []
            for number, text in slides:
                if number <= 12 or any(
                    keyword in text
                    for keyword in ["需求", "思路", "小结", "核心概念", "配置", "事务", "登录", "AOP", "分模块", "Bean", "SQL", "Maven", "SpringBoot"]
                ):
                    picked.append((number, text[:180]))
                if len(picked) >= 14:
                    break
            slide_lines.extend(picked)

        refs = code_files(base)[:10]
        lines: list[str] = []
        lines.append(f"# 第{order:02d}讲：{meta['title']}\n")
        lines.append(f"> 课程来源：{base.name}。本讲整理自配套 PPT 与代码，适合直接用于 SpringBoot 课程课堂讲授、RAG 知识库和课后练习。\n")
        lines.append("## 一、课堂定位\n")
        lines.append(f"{meta['summary']}\n\n**本讲主线：** {meta['thesis']}\n")
        lines.append("## 二、学习目标\n")
        lines.extend(f"- {item}" for item in meta["objectives"])
        lines.append("\n## 三、建议课时与课堂流程\n")
        lines.extend(
            [
                "- 课前 5 分钟：用一个真实问题导入，让学生先说出已有理解。",
                "- 概念讲授 20-30 分钟：围绕 PPT 的主线讲清概念、注解、流程或 SQL。",
                "- 代码演示 25-35 分钟：使用 `ppt/` 中配套代码现场改造或运行。",
                "- 课堂练习 20-30 分钟：让学生补全接口、SQL、配置或切面。",
                "- 复盘 10 分钟：用 AI 助教收集疑问，教师根据薄弱点补讲。",
            ]
        )
        lines.append("\n## 四、核心知识点\n")
        for index, concept in enumerate(meta["concepts"], 1):
            lines.append(f"### {index}. {concept}")
            lines.append("- 讲授建议：先给出业务场景，再落到代码或配置，不建议只背定义。")
            lines.append("- AI 助教追问：请学生解释它解决了什么问题、放在哪一层、错误使用会怎样。")
        lines.append("\n## 五、课堂演示\n")
        lines.extend(f"- {item}" for item in meta["demos"])
        lines.append("\n## 六、课堂练习\n")
        lines.extend(f"- {item}" for item in meta["practice"])
        lines.append("\n## 七、验收标准\n")
        lines.extend(
            [
                "- 能画出本讲相关调用链或数据流。",
                "- 能说明关键注解、SQL、配置或 Maven 坐标的作用。",
                "- 能提交可读的代码片段，并解释失败场景。",
                "- AI 助教回答应能引用本讲资料或对应代码片段。",
            ]
        )
        lines.append("\n## 八、易错点与教师干预\n")
        lines.extend(f"- {item}" for item in meta["pitfalls"])
        lines.append("\n## 九、AI 助教提示词\n")
        lines.extend(
            [
                f"- 学生：我正在学习《{meta['title']}》，请用当前章节资料解释核心流程，并给出一个常见错误。",
                f"- 学生：请根据《{meta['title']}》生成一道课堂练习，要求包含代码骨架和检查清单。",
                f"- 教师：请汇总学生在《{meta['title']}》中最容易混淆的 3 个概念，并给出补讲建议。",
            ]
        )
        lines.append("\n## 十、PPT 来源摘录\n")
        lines.extend(f"- {source}" for source in slide_sources)
        for number, text in slide_lines[:16]:
            lines.append(f"- Slide {number}: {text}")
        lines.append("\n## 十一、配套代码索引\n")
        if refs:
            for path, signals in refs:
                lines.append(f"- `{path}`")
                for signal in signals[:3]:
                    lines.append(f"  - `{signal[:160]}`")
        else:
            lines.append("- 本讲未识别到可直接索引的代码文件，请以 PPT 内容和课堂 SQL/配置演示为主。")

        file = OUT / f"lesson-{order:02d}-{meta['slug']}.md"
        file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        lessons.append({**meta, "order": order, "file": file.name, "sources": slide_sources})

    index_lines = [
        "# SpringBoot AI 辅助教学课程资料索引\n",
        "本目录由 `ppt/` 中的 SpringBoot 后端课程 PPT 和配套代码整理而来，可直接用于课堂讲义、AI 助教 RAG 知识库、练习反馈与教师备课。\n",
        "## 课程总目标\n",
        "- 建立从 Maven 工程、SpringBoot Web、数据库、MyBatis 到完整业务系统的后端开发路径。",
        "- 让学生能围绕 Tlias 智能学习辅助系统完成接口、数据访问、认证、日志和统计功能。",
        "- 将每讲资料拆成可检索的知识块，便于 AI 助教回答时引用课程来源。",
        "- 服务教学改革 demo：学生练习、AI 反馈、教师学情分析形成闭环。\n",
        "## 章节清单\n",
    ]
    for lesson in lessons:
        index_lines.append(f"{lesson['order']}. [{lesson['title']}]({lesson['file']})：{lesson['summary']}")
    index_lines.extend(
        [
            "\n## 建议教学路径\n",
            "- 基础阶段：第 01-04 讲，完成 Maven、SpringBoot Web、MySQL、MyBatis。",
            "- 实战阶段：第 05-10 讲，围绕 Tlias 完成部门、员工、班级、学员和登录认证。",
            "- 进阶阶段：第 11-12 讲，完成 AOP 日志、SpringBoot 原理和 Maven 多模块。",
            "- AI 教改融合：每讲都加入“AI 助教提示词”和“验收标准”，便于学生即时提问与教师复盘。\n",
            "## RAG 使用说明\n",
            "- 每个 Markdown 文件都保留了 PPT 来源、页码摘录和代码路径。",
            "- 后端可以按文件切块导入，回答时引用 `docs/course-materials/lesson-xx-*.md`。",
            "- 建议教师先用 `rag-seed.md` 快速初始化知识库，再按需上传单讲资料。",
            "- 不包含任何真实 API Key 或敏感配置。",
        ]
    )
    (OUT / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    rag_lines = ["# SpringBoot 课程 RAG 合并知识库\n"]
    for lesson in lessons:
        rag_lines.extend(
            [
                f"\n## 第{lesson['order']:02d}讲：{lesson['title']}\n",
                f"来源文件：{lesson['file']}",
                f"课程来源：{'；'.join(lesson['sources'])}",
                f"摘要：{lesson['summary']}",
                "学习目标：",
            ]
        )
        rag_lines.extend(f"- {item}" for item in lesson["objectives"])
        rag_lines.append("课堂练习：")
        rag_lines.extend(f"- {item}" for item in lesson["practice"])
    (OUT / "rag-seed.md").write_text("\n".join(rag_lines) + "\n", encoding="utf-8")

    manifest = {
        "lessons": [
            {
                "order": lesson["order"],
                "slug": lesson["slug"],
                "title": lesson["title"],
                "file": lesson["file"],
                "summary": lesson["summary"],
                "sources": lesson["sources"],
            }
            for lesson in lessons
        ]
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(lessons)} lessons to {OUT}")


if __name__ == "__main__":
    write_materials()
