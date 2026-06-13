import math
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from backend.app.config import ROOT_DIR, get_settings
from backend.app.data.courses import NONGBO_COURSE_ID, SPRINGBOOT_COURSE_ID, get_all_lessons, get_lessons
from backend.app.models import Citation


TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_+-]*|\d+|[\u4e00-\u9fff]+")
PROJECT_ROOT = ROOT_DIR / "农博后台管理系统项目1-5-20260609" / "农博后台管理系统项目1-5"
COURSE_MATERIALS_DIR = ROOT_DIR / "docs" / "course-materials"
COURSE_STANDARD_DOC = ROOT_DIR / "孙立晔+《Web系统应用开发一》+课程标准_24软.doc"
ROOT_NONGBO_SQL = ROOT_DIR / "nb_database.sql"


@dataclass
class KnowledgeChunk:
    id: str
    title: str
    source: str
    text: str
    course_id: str | None = None
    lesson_id: str | None = None
    kind: str = "content"
    keywords: tuple[str, ...] = ()


class RagService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._chunks: list[KnowledgeChunk] = []
        self._chroma_collection = None
        self._backend = "keyword"
        self.ingest_seed()

    @property
    def backend_name(self) -> str:
        return self._backend

    def status(self) -> dict:
        kind_counts = Counter(chunk.kind for chunk in self._chunks)
        course_counts = Counter(chunk.course_id or "shared" for chunk in self._chunks)
        return {
            "backend": self._backend,
            "configured_backend": self.settings.rag_backend,
            "collection": self.settings.rag_collection,
            "chunks": len(self._chunks),
            "top_k": self.settings.rag_top_k,
            "chunk_size": self.settings.rag_chunk_size,
            "snippet_size": self.settings.rag_snippet_size,
            "lesson_boost": self.settings.rag_lesson_boost,
            "concept_boost": self.settings.rag_concept_boost,
            "vector_candidates": self.settings.rag_vector_candidates,
            "structured_concepts": 0,
            "vector_enabled": self._chroma_collection is not None,
            "kind_counts": dict(kind_counts),
            "course_counts": dict(course_counts),
        }

    def ingest_seed(self) -> int:
        chunks: list[KnowledgeChunk] = []
        for lesson in get_all_lessons():
            chunks.append(
                KnowledgeChunk(
                    id=f"{lesson.course_id}:{lesson.id}:lesson",
                    course_id=lesson.course_id,
                    lesson_id=lesson.id,
                    title=lesson.title,
                    source=lesson.source or f"course/{lesson.id}",
                    text="\n".join([lesson.title, lesson.summary, lesson.content, *lesson.objectives]),
                    kind="lesson",
                    keywords=self._lesson_keywords(lesson.course_id, lesson.id),
                )
            )
            chunks.append(
                KnowledgeChunk(
                    id=f"{lesson.course_id}:{lesson.id}:practice",
                    course_id=lesson.course_id,
                    lesson_id=lesson.id,
                    title=f"{lesson.title} - 练习与验收",
                    source=lesson.source or f"course/{lesson.id}",
                    text="\n".join(
                        [
                            lesson.practice.title,
                            lesson.practice.description,
                            lesson.practice.template,
                            *lesson.practice.checklist,
                        ]
                    ),
                    kind="practice",
                    keywords=self._lesson_keywords(lesson.course_id, lesson.id),
                )
            )

        chunks.extend(self._course_material_chunks())
        chunks.extend(self._project_document_chunks())
        chunks.extend(self._sql_schema_chunks())
        chunks.extend(self._standard_chunks())
        chunks.extend(self._course_standard_doc_chunks())
        chunks.extend(self._requirement_spec_chunks())
        self._chunks = [chunk for chunk in chunks if chunk.text.strip()]
        self._try_init_chroma(self._chunks)
        return len(self._chunks)

    def add_document(self, filename: str, content: str, course_id: str | None = None) -> int:
        new_chunks = [
            KnowledgeChunk(
                id=f"upload:{filename}:{index}",
                course_id=course_id,
                title=filename,
                source=f"upload/{filename}",
                text=part,
                kind="upload",
                keywords=tuple(self._tokens(part).keys())[:12],
            )
            for index, part in enumerate(self._split_text(content, self.settings.rag_chunk_size))
            if part.strip()
        ]
        self._chunks.extend(new_chunks)
        self._try_init_chroma(self._chunks)
        return len(new_chunks)

    def search(
        self,
        query: str,
        limit: int | None = None,
        lesson_id: str | None = None,
        course_id: str | None = None,
    ) -> list[Citation]:
        query = self._expand_query(query)
        top_k = limit or self.settings.rag_top_k
        scored: dict[str, tuple[float, KnowledgeChunk]] = {}
        for score, chunk in self._keyword_rank(query, lesson_id, course_id):
            if score > 0:
                scored[chunk.id] = (score, chunk)

        if self._chroma_collection is not None:
            try:
                n_results = max(top_k, self.settings.rag_vector_candidates)
                result = self._chroma_collection.query(
                    query_texts=[self._rewrite_query(query, lesson_id, course_id)],
                    n_results=n_results,
                )
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                distances = result.get("distances", [[]])[0]
                for doc, meta, distance in zip(docs, metas, distances, strict=False):
                    chunk_id = meta.get("id", "")
                    chunk = self._chunk_by_id(chunk_id) or KnowledgeChunk(
                        id=chunk_id,
                        title=meta.get("title", "知识库资料"),
                        source=meta.get("source", "knowledge-base"),
                        text=doc,
                        course_id=meta.get("course_id") or None,
                        lesson_id=meta.get("lesson_id") or None,
                        kind=meta.get("kind", "chunk"),
                    )
                    if not self._allowed(chunk, course_id):
                        continue
                    if self._score(query, doc) <= 0 and not self._keyword_hits(query, chunk.keywords):
                        continue
                    vector_score = (1 / (1 + max(float(distance), 0))) + self._context_boost(query, chunk, lesson_id, course_id)
                    current = scored.get(chunk.id, (0, chunk))[0]
                    scored[chunk.id] = (max(current, vector_score), chunk)
            except Exception:
                self._chroma_collection = None
                self._backend = "keyword"

        ranked = sorted(scored.values(), key=lambda item: item[0], reverse=True)
        source_ranked = [
            item for item in ranked
            if item[1].kind not in {"lesson", "practice"}
        ]
        selected = source_ranked if source_ranked else ranked
        selected = self._filter_concept_results(query, selected)
        return [self._to_citation(chunk, score, query) for score, chunk in selected[:top_k] if score > 0]

    def _try_init_chroma(self, chunks: list[KnowledgeChunk]) -> None:
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            client = chromadb.PersistentClient(path=str(self.settings.chroma_dir))
            embedder = embedding_functions.ONNXMiniLM_L6_V2()
            collection = client.get_or_create_collection(self.settings.rag_collection, embedding_function=embedder)
            existing_ids = collection.get(include=[])["ids"] if collection.count() else []
            if existing_ids:
                collection.delete(ids=existing_ids)
            collection.add(
                ids=[chunk.id for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                metadatas=[
                    {
                        "id": chunk.id,
                        "title": chunk.title,
                        "source": chunk.source,
                        "course_id": chunk.course_id or "",
                        "lesson_id": chunk.lesson_id or "",
                        "kind": chunk.kind,
                    }
                    for chunk in chunks
                ],
            )
            self._chroma_collection = collection if self.settings.rag_backend != "keyword" else None
            self._backend = "hybrid" if self._chroma_collection is not None else "keyword"
        except Exception:
            self._chroma_collection = None
            self._backend = "keyword"

    def _keyword_rank(self, query: str, lesson_id: str | None, course_id: str | None) -> list[tuple[float, KnowledgeChunk]]:
        ranked = []
        for chunk in self._chunks:
            if not self._allowed(chunk, course_id):
                continue
            base_score = self._score(query, chunk.text)
            if base_score <= 0 and not self._keyword_hits(query, chunk.keywords):
                continue
            ranked.append((base_score + self._concept_boost(query, chunk.text) + self._context_boost(query, chunk, lesson_id, course_id), chunk))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked

    def _allowed(self, chunk: KnowledgeChunk, course_id: str | None) -> bool:
        if course_id is None:
            return True
        return chunk.course_id in (None, course_id)

    def _context_boost(self, query: str, chunk: KnowledgeChunk, lesson_id: str | None, course_id: str | None) -> float:
        boost = 0.0
        if course_id and chunk.course_id == course_id:
            boost += 0.08
        if lesson_id and chunk.lesson_id == lesson_id:
            boost += self.settings.rag_lesson_boost
        if self._keyword_hits(query, chunk.keywords):
            boost += 0.12
        return boost

    def _score(self, query: str, text: str) -> float:
        query_tokens = self._tokens(query)
        text_tokens = self._tokens(text)
        if not query_tokens or not text_tokens:
            return 0
        overlap = sum(min(query_tokens.get(token, 0), text_tokens.get(token, 0)) for token in query_tokens)
        return overlap / math.sqrt(sum(text_tokens.values()))

    def _concept_boost(self, query: str, text: str) -> float:
        lowered_query = query.lower()
        lowered_text = text.lower()
        boost = 0.0
        if ("ioc" in lowered_query or "控制反转" in lowered_query) and "控制反转" in lowered_text:
            boost += 2.0
        if ("di" in lowered_query or "依赖注入" in lowered_query) and "依赖注入" in lowered_text:
            boost += 1.5
        if "对象的创建权" in lowered_text or "spring 容器" in lowered_text:
            boost += 0.8
        return boost

    def _filter_concept_results(self, query: str, ranked: list[tuple[float, KnowledgeChunk]]) -> list[tuple[float, KnowledgeChunk]]:
        lowered_query = query.lower()
        if not re.search(r"\bioc\b|控制反转|依赖注入|\bdi\b", lowered_query):
            return ranked
        strong_terms = ("ioc", "控制反转", "依赖注入", "autowired", "bean", "spring 容器")
        filtered = [
            item for item in ranked
            if any(term in f"{item[1].title} {item[1].text}".lower() for term in strong_terms)
        ]
        return filtered or ranked

    def _tokens(self, text: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for token in TOKEN_PATTERN.findall(text.lower()):
            counts[token] = counts.get(token, 0) + 1
            if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                for size in (2, 3, 4):
                    for index in range(0, max(0, len(token) - size + 1)):
                        part = token[index:index + size]
                        counts[part] = counts.get(part, 0) + 1
        return counts

    def _expand_query(self, query: str) -> str:
        lowered = query.lower()
        expansions = []
        if re.search(r"\bioc\b|控制反转", lowered):
            expansions.extend(["ioc", "控制反转", "依赖注入", "di", "spring 容器", "Autowired", "Bean"])
        if re.search(r"\bdi\b|依赖注入", lowered):
            expansions.extend(["di", "依赖注入", "ioc", "Autowired", "Bean"])
        if "交付物" in query or "交付" in query:
            expansions.extend(["交付内容", "验收标准", "项目需求分析", "技术方案规划", "数据库规划", "接口规范"])
        if "项目1" in query:
            expansions.extend(["项目1", "需求与技术方案", "需求分析", "技术方案", "数据库规划", "接口规范"])
        return " ".join([query, *expansions])

    def _split_text(self, text: str, size: int) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) > size and current:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n\n{paragraph}".strip()
        if current:
            chunks.append(current)
        return chunks or ([text[:size]] if text else [])

    def _course_material_chunks(self) -> list[KnowledgeChunk]:
        if not COURSE_MATERIALS_DIR.exists():
            return []
        chunks: list[KnowledgeChunk] = []
        lesson_by_source = {lesson.source: lesson for lesson in get_lessons(SPRINGBOOT_COURSE_ID)}
        for path in sorted(COURSE_MATERIALS_DIR.glob("*.md")):
            content = self._read_text(path)
            if not content.strip():
                continue
            source = self._rel(path)
            lesson = lesson_by_source.get(source)
            for index, part in enumerate(self._split_text(content, self.settings.rag_chunk_size)):
                chunks.append(
                    KnowledgeChunk(
                        id=f"springboot-doc:{path.stem}:{index}",
                        course_id=SPRINGBOOT_COURSE_ID,
                        lesson_id=lesson.id if lesson else None,
                        title=self._material_title(content, path.stem),
                        source=source,
                        text=part,
                        kind="course-material",
                        keywords=tuple(self._tokens(part).keys())[:16],
                    )
                )
        return chunks

    def _project_document_chunks(self) -> list[KnowledgeChunk]:
        if not PROJECT_ROOT.exists():
            return []
        chunks: list[KnowledgeChunk] = []
        for path in sorted(PROJECT_ROOT.rglob("*.md")):
            if self._ignored_path(path):
                continue
            content = self._read_text(path)
            if not content.strip():
                continue
            for index, part in enumerate(self._split_text(content, self.settings.rag_chunk_size)):
                chunks.append(
                    KnowledgeChunk(
                        id=f"nongbo-doc:{path.stem}:{index}",
                        course_id=NONGBO_COURSE_ID,
                        title=self._material_title(content, path.stem),
                        source=self._rel(path),
                        text=part,
                        kind="project-document",
                        keywords=tuple(self._tokens(part).keys())[:16],
                    )
                )
        return chunks

    def _sql_schema_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for sql_path in [ROOT_NONGBO_SQL, PROJECT_ROOT / "nb_database.sql"]:
            content = self._read_text(sql_path)
            if not content.strip():
                continue
            source_key = "root" if sql_path == ROOT_NONGBO_SQL else "project"
            for match in re.finditer(r"CREATE TABLE `(?P<table>[^`]+)`\s+\((?P<body>.*?)\)\s+ENGINE", content, re.S):
                table = match.group("table")
                body = match.group("body")
                text = f"表 `{table}` 结构：\n{body}"
                chunks.append(
                    KnowledgeChunk(
                        id=f"nongbo-sql:{source_key}:{table}",
                        course_id=NONGBO_COURSE_ID,
                        title=f"{table} 表结构",
                        source=self._rel(sql_path),
                        text=text,
                        kind="database-schema",
                        keywords=tuple(self._tokens(text).keys())[:16],
                    )
                )
        return chunks

    def _course_standard_doc_chunks(self) -> list[KnowledgeChunk]:
        text = self._read_legacy_doc_text(COURSE_STANDARD_DOC)
        if not text.strip():
            return []
        return [
            KnowledgeChunk(
                id=f"web-course-standard:{index}",
                course_id=NONGBO_COURSE_ID,
                title="《Web应用系统开发一》课程标准",
                source=self._rel(COURSE_STANDARD_DOC),
                text=part,
                kind="course-standard",
                keywords=tuple(self._tokens(part).keys())[:16],
            )
            for index, part in enumerate(self._split_text(text, self.settings.rag_chunk_size))
        ]

    def _standard_chunks(self) -> list[KnowledgeChunk]:
        try:
            from pypdf import PdfReader

            pdf = next(ROOT_DIR.glob("301*.pdf"))
            reader = PdfReader(str(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return []
        return [
            KnowledgeChunk(
                id=f"javaweb-standard:{index}",
                course_id=None,
                title="JavaWeb 应用开发职业技能等级标准",
                source=self._rel(pdf),
                text=part,
                kind="standard",
                keywords=tuple(self._tokens(part).keys())[:16],
            )
            for index, part in enumerate(self._split_text(text, self.settings.rag_chunk_size))
        ]

    def _requirement_spec_chunks(self) -> list[KnowledgeChunk]:
        try:
            docx = next(ROOT_DIR.glob("*.docx"))
            with zipfile.ZipFile(docx) as archive:
                xml = archive.read("word/document.xml")
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            root = ET.fromstring(xml)
            paragraphs = []
            for paragraph in root.findall(".//w:p", ns):
                line = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
                if line:
                    paragraphs.append(line)
            text = "\n".join(paragraphs)
        except Exception:
            return []
        start_candidates = [text.find("PC后台功能需求规格说明"), text.find("首页通用模块"), text.find("用户管理")]
        starts = [index for index in start_candidates if index >= 0]
        start = min(starts) if starts else 0
        end = text.find("非功能性需求", start)
        pc_text = text[start: end if end > start else min(len(text), start + 60000)]
        return [
            KnowledgeChunk(
                id=f"nongbo-requirement:{index}",
                course_id=NONGBO_COURSE_ID,
                title="农宝系统需求规格说明书 PC 后台章节",
                source=self._rel(docx),
                text=part,
                kind="requirement-spec",
                keywords=tuple(self._tokens(part).keys())[:16],
            )
            for index, part in enumerate(self._split_text(pc_text, self.settings.rag_chunk_size))
        ]

    def _material_title(self, content: str, fallback: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
        return fallback

    def _snippet(self, text: str, limit: int | None = None, query: str = "") -> str:
        limit = limit or self.settings.rag_snippet_size
        compact = " ".join(text.split())
        lowered = compact.lower()
        terms = [term for term in ["控制反转", "依赖注入", "ioc", "di", "autowired", "bean"] if term in query.lower()]
        positions = [lowered.find(term.lower()) for term in terms if lowered.find(term.lower()) >= 0]
        if positions:
            start = min(positions)
            compact = compact[start:]
        return compact[:limit] + ("..." if len(compact) > limit else "")

    def _to_citation(self, chunk: KnowledgeChunk, score: float, query: str = "") -> Citation:
        return Citation(
            title=chunk.title,
            source=chunk.source,
            snippet=self._snippet(chunk.text, query=query),
            score=round(float(score), 4),
            course_id=chunk.course_id,
            lesson_id=chunk.lesson_id,
            kind=chunk.kind,
        )

    def _chunk_by_id(self, chunk_id: str) -> KnowledgeChunk | None:
        for chunk in self._chunks:
            if chunk.id == chunk_id:
                return chunk
        return None

    def _rewrite_query(self, query: str, lesson_id: str | None, course_id: str | None) -> str:
        keywords = " ".join(self._lesson_keywords(course_id, lesson_id or ""))
        return f"{course_id or ''} {lesson_id or ''} {query} {keywords}".strip()

    def _lesson_keywords(self, course_id: str | None, lesson_id: str | None) -> tuple[str, ...]:
        for lesson in get_lessons(course_id or SPRINGBOOT_COURSE_ID):
            if lesson.id == lesson_id:
                tokens = [lesson.title, lesson.summary, *lesson.objectives, *lesson.practice.checklist]
                return tuple(self._tokens(" ".join(tokens)).keys())[:18]
        return ()

    def _keyword_hits(self, query: str, keywords: tuple[str, ...]) -> bool:
        lowered = query.lower()
        return any(keyword.lower() in lowered for keyword in keywords if keyword)

    def _ignored_path(self, path: Path) -> bool:
        ignored = {"node_modules", "dist", "uploads", "target", ".git"}
        return any(part in ignored for part in path.parts)

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    def _read_legacy_doc_text(self, path: Path) -> str:
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

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")


rag_service = RagService()
