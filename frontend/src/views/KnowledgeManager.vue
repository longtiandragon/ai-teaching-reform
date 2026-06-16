<template>
  <div class="knowledge-manager">
    <section class="page-header">
      <div>
        <p class="eyebrow">Knowledge Base</p>
        <h2>知识库管理</h2>
        <p>上传、管理和关联课程资料到学习任务。</p>
      </div>
      <el-button type="primary" @click="showUpload = true">
        <Upload :size="16" />
        上传文件
      </el-button>
    </section>

    <!-- 上传对话框 -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal-card">
        <h3>上传知识库文件</h3>
        <p class="modal-desc">支持 PDF、Word、Excel、CSV、Markdown、代码文件等。上传后自动解析并索引。</p>
        <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
          <input ref="fileInput" type="file" accept=".pdf,.docx,.xlsx,.xls,.csv,.md,.markdown,.txt,.java,.py,.js,.ts,.vue,.xml,.yml,.yaml,.json,.sql,.html,.css,.properties,.sh,.toml,.ini,.gitignore,.env" style="display:none" @change="handleFile" />
          <Upload :size="32" />
          <span>点击或拖拽文件到此处</span>
          <small>{{ uploadFile?.name || '未选择文件' }}</small>
        </div>
        <div class="form-field">
          <label>关联课程线</label>
          <select v-model="uploadCourseLine" @change="loadUploadTasks">
            <option value="springboot-course-12">SpringBoot 12 讲</option>
            <option value="nongbo-admin-project">农宝项目</option>
          </select>
        </div>
        <div class="form-field">
          <label>关联任务（推荐）</label>
          <select v-model="uploadTaskId">
            <option value="">仅加入课程知识库</option>
            <option v-for="task in uploadTaskList" :key="task.id" :value="task.id">{{ task.title }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <el-button @click="showUpload = false">取消</el-button>
          <el-button type="primary" @click="doUpload" :loading="uploading" :disabled="!uploadFile">
            上传并索引
          </el-button>
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <section class="file-list panel">
      <div class="panel-title file-title" @click="fileListExpanded = !fileListExpanded">
        <h3>已上传文件</h3>
        <div class="title-right">
          <span class="muted">{{ files.length }} 个文件</span>
          <ChevronDown :size="16" :class="['collapse-icon', { expanded: fileListExpanded }]" />
        </div>
      </div>
      <Transition name="collapse">
        <div v-show="fileListExpanded" class="file-table">
        <div v-if="!files.length" class="empty-state">
          <Database :size="32" />
          <p>暂无文件，请上传知识库资料。</p>
        </div>
        <div v-for="file in files" :key="file.id" class="file-row">
          <FileText :size="16" />
          <span class="file-name">{{ file.filename }}</span>
          <span class="file-meta">{{ file.chunk_count }} chunks</span>
          <span class="file-meta">{{ courseLineLabel(file.course_line_id) }}</span>
          <span class="file-meta">{{ formatDate(file.created_at) }}</span>
          <button class="icon-btn" @click="deleteFile(file.id)" title="删除">
            <Trash2 :size="14" />
          </button>
        </div>
      </div>
      </Transition>
    </section>

    <!-- ========== 题库管理 ========== -->
    <section class="panel question-bank-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Question Bank</p>
          <h3>题库管理</h3>
          <small>{{ questionFilterCourse === 'nongbo-admin-project' ? '农宝项目' : '12讲基础' }} · {{ questionTotal }} 题</small>
        </div>
        <div style="display:flex;gap:8px">
          <select v-model="questionFilterCourse" @change="loadQuestions" style="border:1px solid rgba(0,0,0,0.08);border-radius:8px;padding:6px 10px;font-size:13px;background:var(--bg-card);color:var(--text-primary)">
            <option value="springboot-course-12">12讲基础知识</option>
            <option value="nongbo-admin-project">农宝项目</option>
          </select>
          <el-button type="primary" :icon="Plus" size="small" @click="openAddQuestion">新建题目</el-button>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="question-table-wrap">
        <table class="question-table" v-if="questionList.length">
          <thead>
            <tr>
              <th style="width:60px">类型</th>
              <th style="width:120px">章节</th>
              <th>题干</th>
              <th style="width:70px">难度</th>
              <th style="width:120px">已发布</th>
              <th style="width:130px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questionList" :key="q.id">
              <td><el-tag size="small" :type="qTypeTag(q.type)">{{ qTypeLabel(q.type) }}</el-tag></td>
              <td>{{ lessonLabel(q.lesson_id) }}</td>
              <td class="stem-cell">
                <strong>{{ q.stem }}</strong>
                <div class="answer-preview">答案：{{ q.answer }}</div>
                <div v-if="q.explanation" class="explanation-preview">解析：{{ q.explanation }}</div>
                <button class="btn-sm explain-btn" @click="generateExplanation(q)">AI 生成解析</button>
              </td>
              <td><span :class="`diff-${q.difficulty}`">{{ q.difficulty === 'easy' ? '简单' : q.difficulty === 'medium' ? '中等' : '困难' }}</span></td>
              <td>
                <template v-if="questionPublishedMap[q.id]?.length">
                  <el-tag v-for="pt in questionPublishedMap[q.id]" :key="pt.task_id" size="small" closable @close="handleUnpublish(q.id, pt.task_id)" style="margin:2px">
                    {{ taskTitleMap[pt.task_id] || pt.task_id }}
                  </el-tag>
                </template>
                <span v-else class="muted-text">-</span>
              </td>
              <td>
                <button class="btn-sm publish-btn" @click="openPublish(q)" title="发布到关卡">发布</button>
                <button class="btn-sm" @click="editQuestion(q)">编辑</button>
                <button v-if="!questionPublishedMap[q.id]?.length" class="btn-sm danger" @click="removeQuestion(q.id)">删除</button>
                <span v-else-if="!q.id.startsWith('teacher-')" class="seed-badge">系统题</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">该课程暂无题目。点击"新建题目"添加。</div>
      </div>

      <!-- 新建/编辑题目对话框 -->
      <div v-if="showQuestionForm" class="modal-overlay" @click.self="showQuestionForm = false">
        <div class="modal-card question-modal">
          <h3>{{ editingQuestion ? '编辑题目' : '新建题目' }}</h3>
          <label>章节
            <select v-model="questionForm.lesson_id">
              <option v-for="l in questionLessons" :key="l.id" :value="l.id">{{ l.title }}</option>
            </select>
          </label>
          <label>类型
            <select v-model="questionForm.type">
              <option value="single_choice">单选题</option>
              <option value="multi_choice">多选题</option>
              <option value="true_false">判断题</option>
              <option value="short_answer">简答题</option>
              <option value="code_fill">代码填空</option>
            </select>
          </label>
          <label>难度
            <select v-model="questionForm.difficulty">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </label>
          <label>题干<textarea v-model="questionForm.stem" rows="3" style="width:100%;border:1px solid rgba(0,0,0,0.08);border-radius:8px;padding:8px;font-size:13px" /></label>
          <label v-if="needsOptions(questionForm.type)">
            选项（一行一个，格式：A. 选项文本）
            <textarea v-model="optionsText" rows="4" :placeholder="'A. Result<T> 统一返回\nB. 直接返回 Entity\nC. 返回 String\nD. 返回 Map'" style="width:100%;border:1px solid rgba(0,0,0,0.08);border-radius:8px;padding:8px;font-family:monospace;font-size:13px" />
          </label>
          <label>正确答案<textarea v-model="questionForm.answer" rows="2" style="width:100%;border:1px solid rgba(0,0,0,0.08);border-radius:8px;padding:8px;font-size:13px" :placeholder="needsOptions(questionForm.type) ? '如: A 或 AB' : '简述评分要点或填入正确代码'" /></label>
          <label>解析（可选）<textarea v-model="questionForm.explanation" rows="2" style="width:100%;border:1px solid rgba(0,0,0,0.08);border-radius:8px;padding:8px;font-size:13px" /></label>
          <div style="display:flex;gap:10px;margin-top:14px;justify-content:flex-end">
            <el-button @click="showQuestionForm = false">取消</el-button>
            <el-button type="primary" @click="saveQuestion" :loading="savingQuestion">
              {{ editingQuestion ? '保存修改' : '创建题目' }}
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- 发布到关卡对话框 -->
    <div v-if="showPublishModal" class="modal-overlay" @click.self="showPublishModal = false">
      <div class="modal-card">
        <h3>发布题目到关卡</h3>
        <p class="modal-desc">将"{{ publishingQuestion?.stem?.slice(0, 40) }}..."发布到指定关卡，学生可在该关卡中看到此题。</p>
        <div class="form-field">
          <label>选择课程线</label>
          <select v-model="publishCourseLine" @change="loadPublishTasks">
            <option value="springboot-course-12">SpringBoot 12 讲</option>
            <option value="nongbo-admin-project">农宝项目</option>
          </select>
        </div>
        <div class="form-field">
          <label>选择关卡</label>
          <select v-model="publishTaskId" @change="loadPublishTaskFiles">
            <option value="" disabled>请选择关卡</option>
            <option v-for="t in publishTaskList" :key="t.id" :value="t.id">{{ t.title }}</option>
          </select>
        </div>
        <div :class="['kb-link-status', { warning: !publishTaskFiles.length }]">
          <FileText :size="15" />
          <span v-if="publishTaskFiles.length">
            已关联 {{ publishTaskFiles.length }} 份知识库资料，学生进入智能体模式后会优先引用这些资料。
          </span>
          <span v-else>
            该任务还没有关联资料。请先在上方上传资料并选择同一任务，再发布给学生。
          </span>
        </div>
        <div class="modal-actions">
          <el-button @click="showPublishModal = false">取消</el-button>
          <el-button type="primary" @click="doPublish" :loading="publishing" :disabled="!publishTaskId || !publishTaskFiles.length">
            确认发布
          </el-button>
        </div>
      </div>
    </div>

    <!-- 已发布题目总览 -->
    <section class="panel published-panel" v-if="publishedGrouped.length">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Published Questions</p>
          <h3>已发布题目总览</h3>
          <small>{{ publishedGrouped.length }} 个关卡共有已发布题目</small>
        </div>
      </div>
      <div class="published-groups">
        <div v-for="group in publishedGrouped" :key="group.taskId" class="published-group">
          <div class="group-header">
            <strong>{{ taskTitleMap[group.taskId] || group.taskId }}</strong>
            <span class="muted-text">{{ group.questions.length }} 题</span>
          </div>
          <div class="group-questions">
            <article v-for="q in group.questions" :key="q.id" class="published-q-card">
              <div class="published-q-main">
                <div class="published-q-meta">
                  <el-tag size="small" :type="qTypeTag(q.type)">{{ qTypeLabel(q.type) }}</el-tag>
                  <span :class="`diff-${q.difficulty}`">{{ q.difficulty === 'easy' ? '简单' : q.difficulty === 'medium' ? '中等' : '困难' }}</span>
                </div>
                <strong class="published-q-stem">{{ q.stem }}</strong>
                <div class="published-q-detail">
                  <span class="detail-label">答案</span>
                  <span>{{ q.answer || '未填写' }}</span>
                </div>
                <div class="published-q-detail">
                  <span class="detail-label">解析</span>
                  <span>{{ q.explanation || '未填写解析' }}</span>
                </div>
              </div>
              <div class="published-q-actions">
                <button class="btn-sm" @click="editQuestion(q)">编辑</button>
                <button class="btn-sm explain-btn" @click="generateExplanation(q)">AI 生成解析</button>
                <button class="btn-sm danger" @click="handleUnpublish(q.id, group.taskId)">取消发布</button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Upload, Database, FileText, Trash2, Plus, ChevronDown } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { api, type Question, type QuestionCreatePayload, type QuestionOption, type LearningTaskSummary } from '../api'

const showUpload = ref(false)
const fileListExpanded = ref(true)
const uploading = ref(false)
const uploadFile = ref<File | null>(null)
const uploadCourseLine = ref('nongbo-admin-project')
const uploadTaskId = ref('')
const uploadTaskList = ref<LearningTaskSummary[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

const files = ref<Array<{
  id: string
  filename: string
  file_type: string
  course_line_id: string | null
  chunk_count: number
  created_at: string
}>>([])

onMounted(async () => {
  await loadFiles()
  await loadUploadTasks()
})

async function loadUploadTasks() {
  if (!uploadCourseLine.value) {
    uploadTaskList.value = []
    uploadTaskId.value = ''
    return
  }
  try {
    const map = await api.learningMap(uploadCourseLine.value)
    uploadTaskList.value = map.tasks
    for (const task of map.tasks) {
      taskTitleMap.value[task.id] = task.title
    }
    if (!uploadTaskList.value.some((task) => task.id === uploadTaskId.value)) {
      uploadTaskId.value = uploadTaskList.value[0]?.id || ''
    }
  } catch {
    uploadTaskList.value = []
    uploadTaskId.value = ''
  }
}

async function loadFiles() {
  try {
    const res = await api.kbFiles()
    files.value = res.files
  } catch { /* ignore */ }
}

function triggerUpload() {
  fileInput.value?.click()
}

function handleFile(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.length) {
    uploadFile.value = input.files[0]
  }
}

function handleDrop(event: DragEvent) {
  if (event.dataTransfer?.files.length) {
    uploadFile.value = event.dataTransfer.files[0]
  }
}

async function doUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    await api.uploadKnowledgeFile({
      file: uploadFile.value,
      courseLineId: uploadCourseLine.value,
      taskId: uploadTaskId.value || undefined,
    })
    ElMessage.success(uploadTaskId.value ? '文件已上传、索引并关联到任务' : '文件已上传并索引')
    showUpload.value = false
    uploadFile.value = null
    await loadFiles()
    await loadPublishTaskFiles()
  } catch (e: any) {
    ElMessage.error(`上传失败: ${e.message}`)
  } finally {
    uploading.value = false
  }
}

async function deleteFile(id: string) {
  try {
    await api.kbDeleteFile(id)
    ElMessage.success('已删除')
    await loadFiles()
  } catch {
    ElMessage.error('删除失败')
  }
}

function courseLineLabel(id: string | null) {
  if (!id) return '共享'
  if (id === 'nongbo-admin-project') return '农宝项目'
  return 'SpringBoot 12 讲'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN')
}

// ---------- 题库管理 ----------
const questionFilterCourse = ref('springboot-course-12')
const questionList = ref<Question[]>([])
const questionTotal = ref(0)
const showQuestionForm = ref(false)
const savingQuestion = ref(false)
const editingQuestion = ref<Question | null>(null)
const optionsText = ref('')

const questionForm = ref<QuestionCreatePayload>({
  course_id: 'springboot-course-12',
  lesson_id: '',
  type: 'single_choice',
  stem: '',
  options: null,
  answer: '',
  explanation: '',
  difficulty: 'medium',
  tags: [],
})

const questionLessons = ref<{ id: string; title: string }[]>([])

onMounted(async () => {
  await loadQuestions()
  await loadAllPublished()
})

async function loadQuestions() {
  try {
    const res = await api.questions(questionFilterCourse.value)
    questionList.value = res.questions
    questionTotal.value = res.total
    const seen = new Map<string, string>()
    for (const q of res.questions) {
      if (!seen.has(q.lesson_id)) seen.set(q.lesson_id, lessonLabel(q.lesson_id))
    }
    questionLessons.value = Array.from(seen.entries()).map(([id, title]) => ({ id, title }))
    if (questionLessons.value.length && !questionForm.value.lesson_id) {
      questionForm.value.lesson_id = questionLessons.value[0].id
    }
  } catch { /* ignore */ }
}

function lessonLabel(lid: string) {
  const formalMap: Record<string, string> = {
    'springboot-03-maven-basic': '01 Maven 项目构建',
    'springboot-04-springboot-web-basic': '02 Spring Boot Web 基础',
    'springboot-05-mysql-sql': '03 MySQL 与 SQL',
    'springboot-06-jdbc-mybatis': '04 JDBC 与 MyBatis',
    'springboot-07-dept-management': '05 部门管理 CRUD',
    'springboot-08-emp-query': '06 员工分页查询',
    'springboot-09-emp-save-upload-transaction': '07 文件上传与事务',
    'springboot-10-emp-update-exception-report': '08 异常处理与报表',
    'springboot-11-project-practice': '09 项目综合实践',
    'springboot-12-login-auth': '10 登录认证',
    'springboot-13-aop-log': '11 AOP 操作日志',
    'springboot-14-springboot-principle': '12 Spring Boot 原理',
    'nongbo-login-auth': '农宝项目 - 登录认证',
    'nongbo-produce-crud': '农宝项目 - 农产品 CRUD',
    'nongbo-ad-credit': '农宝项目 - 广告与信用',
    'nongbo-course-expert': '农宝项目 - 课程与专家',
    'nongbo-market-service': '农宝项目 - 市场与服务',
    'nongbo-full-integration': '农宝项目 - 完整联调',
    'task-requirement-understanding': '01 业务需求梳理',
    'task-database-overview': '02 数据库表结构分析',
    'task-ssm-config': '03 SSM 配置文件理解',
    'task-ssm-mapper-xml': '04 Mapper XML 手写 SQL',
    'task-springboot-setup': '05 Spring Boot 项目搭建',
    'task-expert-crud': '06 专家管理 CRUD 开发',
    'task-course-management': '07 图文课程管理开发',
    'task-policy-module': '08 补贴政策模块开发',
    'task-service-module': '09 农事服务模块开发',
    'task-produce-module': '10 农产品与农贸市场模块',
    'task-frontend-integration': '11 Vue 前端联调',
    'task-data-dashboard': '12 数据统计大屏',
    'task-course-table-design': '02 数据库表结构分析',
    'task-entity-design': '05 Spring Boot 项目搭建',
    'task-mapper-service-controller': '04 Mapper XML 手写 SQL',
    'task-api-test-reflection': '11 Vue 前端联调',
    'project5-guided-test': '11 Vue 前端联调',
    'nongbo-project5-guided-test': '11 Vue 前端联调',
  }
  if (formalMap[lid]) return formalMap[lid]
  const map: Record<string, string> = {
    'springboot-03-maven-basic': '01-Maven',
    'springboot-04-springboot-web-basic': '02-DI/IoC',
    'springboot-05-mysql-sql': '03-MySQL',
    'springboot-06-jdbc-mybatis': '04-JDBC',
    'springboot-07-dept-management': '05-CRUD',
    'springboot-08-emp-query': '06-分页',
    'springboot-09-emp-save-upload-transaction': '07-事务',
    'springboot-10-emp-update-exception-report': '08-异常',
    'springboot-11-project-practice': '09-实战',
    'springboot-12-login-auth': '10-认证',
    'springboot-13-aop-log': '11-AOP',
    'springboot-14-springboot-principle': '12-原理',
    'nongbo-login-auth': '农宝-认证',
    'nongbo-produce-crud': '农宝-CRUD',
    'nongbo-ad-credit': '农宝-广告信贷',
    'nongbo-course-expert': '农宝-课程专家',
    'nongbo-market-service': '农宝-市场服务',
    'nongbo-full-integration': '农宝-整合',
  }
  if (lid.startsWith('task-')) return '未命名关卡'
  return map[lid] || lid.replace('springboot-', '').replace('nongbo-', '')
}

function qTypeTag(t: string) { return t === 'code_fill' ? '' : t === 'short_answer' ? 'success' : '' }
function qTypeLabel(t: string) {
  const m: Record<string, string> = { single_choice: '单选', multi_choice: '多选', true_false: '判断', short_answer: '简答', code_fill: '填空' }
  return m[t] || t
}

function needsOptions(t: string) { return ['single_choice', 'multi_choice', 'true_false'].includes(t) }

function openAddQuestion() {
  editingQuestion.value = null
  questionForm.value = {
    course_id: questionFilterCourse.value,
    lesson_id: questionLessons.value[0]?.id || '',
    type: 'single_choice',
    stem: '',
    options: null,
    answer: '',
    explanation: '',
    difficulty: 'medium',
    tags: [],
  }
  optionsText.value = ''
  showQuestionForm.value = true
}

function editQuestion(q: Question) {
  editingQuestion.value = q
  questionFilterCourse.value = q.course_id
  if (!questionLessons.value.some((lesson) => lesson.id === q.lesson_id)) {
    questionLessons.value = [{ id: q.lesson_id, title: lessonLabel(q.lesson_id) }, ...questionLessons.value]
  }
  questionForm.value = {
    course_id: q.course_id,
    lesson_id: q.lesson_id,
    type: q.type,
    stem: q.stem,
    options: q.options ? [...q.options] : null,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    tags: [...q.tags],
  }
  optionsText.value = q.options ? q.options.map(o => `${o.key}. ${o.text}`).join('\n') : ''
  showQuestionForm.value = true
}

async function saveQuestion() {
  savingQuestion.value = true
  try {
    if (needsOptions(questionForm.value.type) && optionsText.value.trim()) {
      const opts: QuestionOption[] = []
      const lines = optionsText.value.trim().split('\n').filter(l => l.trim())
      for (const line of lines) {
        const m = /^([A-D])\.\s*(.+)/.exec(line.trim())
        if (m) opts.push({ key: m[1], text: m[2] })
      }
      questionForm.value.options = opts.length ? opts : null
    } else {
      questionForm.value.options = null
    }

    if (editingQuestion.value) {
      await api.updateQuestion(editingQuestion.value.id, questionForm.value)
      ElMessage.success('题目已更新')
    } else {
      await api.createQuestion(questionForm.value)
      ElMessage.success('题目已创建')
    }
    showQuestionForm.value = false
    await loadQuestions()
    await loadAllPublished()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingQuestion.value = false
  }
}

async function removeQuestion(id: string) {
  try {
    await api.deleteQuestion(id)
    ElMessage.success('已删除')
    await loadQuestions()
    await loadAllPublished()
  } catch {
    ElMessage.error('删除失败')
  }
}

// ---------- 发布题目到关卡 ----------
const showPublishModal = ref(false)
const publishingQuestion = ref<Question | null>(null)
const publishCourseLine = ref('springboot-course-12')
const publishTaskId = ref('')
const publishTaskList = ref<LearningTaskSummary[]>([])
const publishing = ref(false)
const publishTaskFiles = ref<Array<{ id: string; filename: string }>>([])

// Map: question_id -> [{task_id, course_line_id}]
const questionPublishedMap = ref<Record<string, Array<{ task_id: string; course_line_id: string }>>>({})
// Map: task_id -> task title
const taskTitleMap = ref<Record<string, string>>({})

// All published questions grouped by task (for overview section)
const publishedAll = ref<Array<{ taskId: string; questions: Question[] }>>([])

const publishedGrouped = computed(() => publishedAll.value.filter(g => g.questions.length > 0))

async function loadPublishTasks() {
  try {
    const map = await api.learningMap(publishCourseLine.value)
    publishTaskList.value = map.tasks
    for (const t of map.tasks) {
      taskTitleMap.value[t.id] = t.title
    }
    publishTaskId.value = publishTaskList.value[0]?.id || ''
    await loadPublishTaskFiles()
  } catch { /* ignore */ }
}

async function loadPublishTaskFiles() {
  publishTaskFiles.value = []
  if (!publishTaskId.value) return
  try {
    const res = await api.kbTaskFiles(publishTaskId.value)
    publishTaskFiles.value = res.files
  } catch {
    publishTaskFiles.value = []
  }
}

async function generateExplanation(q: Question) {
  try {
    const updated = await api.generateQuestionExplanation(q.id)
    const index = questionList.value.findIndex((item) => item.id === q.id)
    if (index >= 0) questionList.value[index] = updated
    await loadAllPublished()
    ElMessage.success('解析已生成')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '解析生成失败')
  }
}

async function loadAllPublished() {
  try {
    publishedAll.value = []
    const nextPublishedMap: Record<string, Array<{ task_id: string; course_line_id: string }>> = {}
    // Load from both course lines
    for (const clId of ['springboot-course-12', 'nongbo-admin-project']) {
      const res = await api.publishedByCourse(clId)
      // Also load task titles
      const map = await api.learningMap(clId)
      for (const t of map.tasks) {
        taskTitleMap.value[t.id] = t.title
      }
      // Merge results
      for (const group of res.tasks) {
        for (const question of group.questions) {
          if (!nextPublishedMap[question.id]) nextPublishedMap[question.id] = []
          nextPublishedMap[question.id].push({ task_id: group.taskId, course_line_id: clId })
        }
        const existing = publishedAll.value.find(g => g.taskId === group.taskId)
        if (existing) {
          existing.questions = group.questions
        } else {
          publishedAll.value.push(group)
        }
      }
    }
    questionPublishedMap.value = nextPublishedMap
  } catch { /* ignore */ }
}

function openPublish(q: Question) {
  publishingQuestion.value = q
  publishCourseLine.value = q.course_id === 'nongbo-admin-project' ? 'nongbo-admin-project' : 'springboot-course-12'
  showPublishModal.value = true
  loadPublishTasks()
}

async function doPublish() {
  if (!publishingQuestion.value || !publishTaskId.value) return
  if (!publishTaskFiles.value.length) {
    ElMessage.warning('请先为该任务上传并关联知识库资料')
    return
  }
  publishing.value = true
  try {
    await api.publishQuestion(
      publishingQuestion.value.id,
      publishTaskId.value,
      publishCourseLine.value,
      'teacher-20240036',
    )
    ElMessage.success('题目已发布到关卡')
    showPublishModal.value = false
    await loadAllPublished()
  } catch {
    ElMessage.error('发布失败')
  } finally {
    publishing.value = false
  }
}

async function handleUnpublish(questionId: string, taskId: string) {
  try {
    await api.unpublishQuestion(questionId, taskId)
    ElMessage.success('已取消发布')
    await loadAllPublished()
  } catch {
    ElMessage.error('取消发布失败')
  }
}
</script>

<style scoped>
.knowledge-manager {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 22px;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.file-title {
  cursor: pointer;
  user-select: none;
}

.file-title:hover {
  background: rgba(0, 0, 0, 0.02);
}

.title-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-icon {
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  color: var(--text-secondary);
}

.collapse-icon.expanded {
  transform: rotate(180deg);
}

.file-table {
  padding: 12px 20px;
  max-height: 400px;
  overflow-y: auto;
}

.file-table::-webkit-scrollbar {
  width: 6px;
}

.file-table::-webkit-scrollbar-track {
  background: transparent;
}

.file-table::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.file-table::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 折叠动画 */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 500px;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  font-size: 14px;
  color: var(--text-primary);
}

.file-name {
  flex: 1;
  font-weight: 500;
}

.file-meta {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 60px;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
}

.icon-btn:hover {
  background: var(--bg-secondary);
  color: var(--accent-danger, #FF8B8B);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px;
  color: var(--text-secondary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
}

.modal-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 26px 30px;
  width: min(480px, 92vw);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
}

.modal-card h3 {
  margin: 0 0 8px;
  color: var(--text-primary);
}

.modal-desc {
  margin: 0 0 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px;
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: border-color 0.2s;
  margin-bottom: 16px;
}

.upload-area:hover {
  border-color: var(--accent-primary);
}

.upload-area small {
  font-size: 12px;
  color: var(--text-secondary);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-field select {
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  outline: none;
}

.kb-link-status {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 4px 0 16px;
  padding: 10px 12px;
  border: 1px solid rgba(32, 165, 121, 0.18);
  border-radius: 8px;
  background: rgba(32, 165, 121, 0.06);
  color: var(--text-primary);
  font-size: 13px;
  line-height: 1.5;
}

.kb-link-status.warning {
  border-color: rgba(217, 119, 6, 0.22);
  background: rgba(217, 119, 6, 0.07);
  color: #92400e;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* ---------- 题库管理 ---------- */
.question-bank-panel {
  margin-top: 4px;
}
.question-bank-panel small {
  color: var(--text-secondary);
  font-size: 13px;
}
.question-table-wrap { max-height: 400px; overflow: auto; }
.question-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.question-table th { background: var(--bg-secondary); padding: 10px 12px; text-align: left; font-weight: 700; color: var(--text-primary); position: sticky; top: 0; }
.question-table td { padding: 10px 12px; border-bottom: 1px solid rgba(0,0,0,0.04); vertical-align: top; color: var(--text-primary); }
.stem-cell { max-width: 360px; white-space: normal; line-height: 1.5; }
.stem-cell strong { display: block; margin-bottom: 6px; }
.answer-preview,
.explanation-preview {
  margin-top: 4px;
  padding: 6px 8px;
  border-radius: 6px;
  background: rgba(0,0,0,0.025);
  color: var(--text-secondary);
  font-size: 12px;
}
.explain-btn { margin-top: 6px; color: #2563eb; border-color: rgba(37,99,235,0.2); }
.diff-easy { color: #20a579; font-weight: 600; }
.diff-medium { color: #d46b08; font-weight: 600; }
.diff-hard { color: #e03131; font-weight: 600; }
.seed-badge { color: var(--accent-primary); font-size: 12px; font-weight: 700; }
.btn-sm { border: 1px solid rgba(0,0,0,0.08); background: var(--bg-card); border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 12px; margin-right: 6px; color: var(--text-primary); transition: all 0.2s; }
.btn-sm:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
.btn-sm.danger { color: #e03131; }
.btn-sm.danger:hover { border-color: #e03131; background: rgba(224,49,49,0.06); }

.question-modal { width: min(600px, 92vw); }
.question-modal h3 { margin-bottom: 16px; color: var(--text-primary); }
.question-modal label { display: block; margin-bottom: 12px; color: var(--text-primary); font-weight: 600; font-size: 13px; }
.question-modal select { width: 100%; border: 1px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 7px 10px; margin-top: 4px; background: var(--bg-card); color: var(--text-primary); }

.publish-btn { color: #D97706; border-color: rgba(217,119,6,0.2); }
.publish-btn:hover { background: rgba(217,119,6,0.06); border-color: #D97706; }
.muted-text { color: var(--text-secondary); font-size: 12px; }

/* ---------- 已发布题目总览 ---------- */
.published-panel { margin-top: 4px; }
.published-panel small { color: var(--text-secondary); font-size: 13px; }
.published-groups { padding: 12px 20px; display: flex; flex-direction: column; gap: 16px; }
.published-group { border: 1px solid rgba(0,0,0,0.04); border-radius: 10px; overflow: hidden; }
.group-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(0,0,0,0.02); font-size: 14px; }
.group-header strong { color: var(--text-primary); }
.group-questions { padding: 10px 14px 14px; display: flex; flex-direction: column; gap: 10px; }
.published-q-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  padding: 12px;
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 8px;
  background: rgba(255,255,255,0.56);
}
.published-q-main { min-width: 0; display: flex; flex-direction: column; gap: 8px; }
.published-q-meta { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.published-q-stem { color: var(--text-primary); line-height: 1.55; word-break: break-word; }
.published-q-detail {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 8px;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.55;
  word-break: break-word;
}
.detail-label {
  color: var(--text-primary);
  font-weight: 700;
}
.published-q-actions {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 6px;
  flex-wrap: wrap;
  max-width: 220px;
}
@media (max-width: 760px) {
  .published-q-card { grid-template-columns: 1fr; }
  .published-q-actions { justify-content: flex-start; max-width: none; }
}
</style>
