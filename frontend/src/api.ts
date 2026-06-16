import axios from 'axios'

const TOKEN_KEY = 'web-training-access-token'

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface Citation {
  title: string
  source: string
  snippet: string
  score: number
  course_id?: string
  lesson_id?: string
  kind: string
}

export interface LessonSummary {
  id: string
  title: string
  duration: string
  status: 'done' | 'active' | 'locked'
  tags: string[]
  source?: string
}

export interface Course {
  id: string
  title: string
  subtitle: string
  progress: number
  lessons: LessonSummary[]
}

export interface ClassInfo {
  id: string
  name: string
  course_id: string
}

export interface UserInfo {
  id: string
  name: string
  role: 'student' | 'teacher'
  class_id?: string | null
  class_name?: string | null
  student_no?: string | null
  username?: string | null
}

export interface LearningRecord {
  id: number
  student_id: string
  class_id?: string | null
  course_id: string
  lesson_id: string
  lesson_title?: string | null
  kind: string
  score?: number | null
  correct?: number | null
  total?: number | null
  code?: string | null
  notes?: string | null
  feedback?: string | null
  answers: Record<string, unknown>[]
  created_at: string
}

export interface Lesson {
  id: string
  course_id?: string
  title: string
  summary: string
  objectives: string[]
  content: string
  practice: {
    title: string
    description: string
    template: string
    checklist: string[]
  }
  source?: string
}

export interface AgentSkill {
  name: string
  title: string
  description: string
  input_schema: Record<string, unknown>
  output_type: string
}

export interface CourseLine {
  id: string
  slug: string
  title: string
  description: string
  target_audience: string
  tech_stack: string[]
  status: string
}

export interface LearningTaskSummary {
  id: string
  module_id: string
  course_line_id: string
  title: string
  type: string
  status: 'completed' | 'active' | 'locked' | 'needs_revision'
  progress: number
  score?: number | null
  required_artifact_type: string
}

export interface LearningModuleSummary {
  id: string
  course_line_id: string
  title: string
  description: string
  business_context: string
  progress: number
  tasks: LearningTaskSummary[]
}

export interface LearningMap {
  courseLineId: string
  title: string
  description: string
  currentModule?: { id: string; title: string } | null
  modules: LearningModuleSummary[]
  tasks: LearningTaskSummary[]
}

export interface LearningTaskDetail {
  id: string
  module_id: string
  course_line_id: string
  title: string
  type: string
  goal: string
  scenario: string
  instruction: string
  required_artifact_type: string
  difficulty: number
  unlock_policy: Record<string, any>
  rubrics: Array<Record<string, any>>
}

export interface RubricScore {
  criterion_id: string
  name: string
  type: string
  required: boolean
  passed: boolean
  score: number
  weight: number
  reason: string
}

export interface AICheckResult {
  passed: boolean
  score: number
  level: 'passed' | 'needs_revision' | 'blocked'
  reply: string
  strengths: string[]
  problems: Array<{ type: string; message: string; suggestion: string }>
  nextActions: string[]
  evidence: Citation[]
  rubricScores: RubricScore[]
  nextTaskUnlocked: boolean
}

export interface TaskSubmissionSnapshot {
  id: number
  studentId: string
  courseLineId: string
  moduleId: string
  taskId: string
  questionId?: string | null
  artifactType?: string | null
  studentInput: string
  createdAt: string
  result: AICheckResult
}

// ---------- 题库 ----------
export interface QuestionOption {
  key: string       // "A" / "B" / "C" / "D"
  text: string
}

export interface Question {
  id: string
  course_id: string
  lesson_id: string
  type: 'single_choice' | 'multi_choice' | 'true_false' | 'short_answer' | 'code_fill'
  stem: string
  options: QuestionOption[] | null
  answer: string
  explanation: string | null
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
}

export interface QuestionCreatePayload {
  course_id: string
  lesson_id: string
  type: string
  stem: string
  options: QuestionOption[] | null
  answer: string
  explanation?: string | null
  difficulty?: string
  tags?: string[]
}

export const api = {
  async health() {
    return (await axios.get('/api/health')).data
  },
  async courses(): Promise<Course[]> {
    return (await axios.get('/api/courses')).data.courses
  },
  async sessionBootstrap(): Promise<{ classes: ClassInfo[]; users: UserInfo[] }> {
    return (await axios.get('/api/session/bootstrap')).data
  },
  async login(account: string, password: string): Promise<{ user: UserInfo; access_token: string; token_type: string }> {
    return (await axios.post('/api/session/login', { account, password })).data
  },
  async lesson(courseId: string, lessonId: string): Promise<Lesson> {
    return (await axios.get(`/api/courses/${courseId}/lessons/${lessonId}`)).data.lesson
  },
  async courseLines(): Promise<CourseLine[]> {
    return (await axios.get('/api/course-lines')).data
  },
  async learningMap(courseLineId: string, studentId?: string): Promise<LearningMap> {
    const params = new URLSearchParams()
    if (studentId) params.set('student_id', studentId)
    const query = params.toString()
    return (await axios.get(`/api/course-lines/${courseLineId}/learning-map${query ? `?${query}` : ''}`)).data
  },
  async learningTask(taskId: string): Promise<LearningTaskDetail> {
    return (await axios.get(`/api/tasks/${taskId}`)).data
  },
  async latestTaskSubmission(taskId: string, studentId: string, questionId?: string): Promise<{ submission: TaskSubmissionSnapshot | null }> {
    const params = new URLSearchParams({ student_id: studentId })
    if (questionId) params.set('question_id', questionId)
    return (await axios.get(`/api/tasks/${taskId}/latest-submission?${params.toString()}`)).data
  },
  async latestQuestionSubmissions(courseLineId: string, studentId: string): Promise<{ submissions: TaskSubmissionSnapshot[] }> {
    const params = new URLSearchParams({ student_id: studentId })
    return (await axios.get(`/api/course-lines/${courseLineId}/latest-question-submissions?${params.toString()}`)).data
  },
  async aiCheck(payload: {
    courseLineId: string
    moduleId: string
    taskId: string
    studentId: string
    artifactType?: string
    studentInput: string
    questionId?: string
    attachments?: Record<string, unknown>[]
    chatHistory?: Record<string, unknown>[]
  }): Promise<AICheckResult> {
    return (await axios.post('/api/ai/check', payload)).data
  },
  async recordLocalCheck(payload: {
    courseLineId: string
    moduleId: string
    taskId: string
    studentId: string
    artifactType?: string
    studentInput: string
    questionId?: string
    result: AICheckResult
  }): Promise<{ ok: boolean }> {
    return (await axios.post('/api/ai/local-check-record', payload)).data
  },
  async aiTaskChat(payload: {
    courseLineId: string
    moduleId?: string
    taskId?: string
    studentId?: string
    question: string
    chatHistory?: Record<string, unknown>[]
  }) {
    return (await axios.post('/api/ai/chat', payload)).data
  },
  async chat(payload: { course_id: string; lesson_id?: string; question: string; mode?: string }) {
    return (await axios.post('/api/chat', payload)).data
  },
  async streamChat(
    payload: { course_id: string; lesson_id?: string; question: string; mode?: string },
    handlers: {
      onStatus?: (data: any) => void
      onCitations?: (citations: Citation[]) => void
      onDelta?: (text: string) => void
      onDone?: (data: any) => void
      onError?: (data: any) => void
    },
  ) {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify(payload),
    })
    if (!response.ok || !response.body) {
      const text = await response.text().catch(() => '')
      throw new Error(text || `stream request failed: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''
      for (const eventText of events) {
        const parsed = parseSseEvent(eventText)
        if (!parsed) continue
        if (parsed.event === 'status') handlers.onStatus?.(parsed.data)
        if (parsed.event === 'citations') handlers.onCitations?.(parsed.data.citations || [])
        if (parsed.event === 'delta') handlers.onDelta?.(parsed.data.text || '')
        if (parsed.event === 'done') handlers.onDone?.(parsed.data)
        if (parsed.event === 'error') handlers.onError?.(parsed.data)
      }
    }
  },
  async submitPractice(payload: { course_id: string; lesson_id: string; code: string; notes: string; student_id?: string }) {
    return (await axios.post('/api/practice/submit', payload)).data
  },
  async submitSelfCheck(payload: {
    student_id: string
    course_id: string
    lesson_id: string
    score: number
    correct: number
    total: number
    answers: Record<string, unknown>[]
  }) {
    return (await axios.post('/api/learning/self-check', payload)).data
  },
  async studentRecords(studentId: string, courseId?: string): Promise<{ records: LearningRecord[] }> {
    const params = new URLSearchParams()
    if (courseId) params.set('course_id', courseId)
    const query = params.toString()
    return (await axios.get(`/api/students/${studentId}/records${query ? `?${query}` : ''}`)).data
  },
  async ingest() {
    return (await axios.post('/api/kb/ingest')).data
  },
  async uploadKnowledgeFile(payload: { file: File; courseLineId?: string; taskId?: string }) {
    const formData = new FormData()
    formData.append('file', payload.file)
    if (payload.courseLineId) formData.append('courseLineId', payload.courseLineId)
    if (payload.taskId) formData.append('taskId', payload.taskId)
    return (await axios.post('/api/kb/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data
  },
  async analytics(studentId?: string) {
    const params = studentId ? '?student_id=' + studentId : ''
    return (await axios.get('/api/teacher/analytics' + params)).data
  },
  async skills(): Promise<AgentSkill[]> {
    return (await axios.get('/api/agent/skills')).data.skills
  },
  async runSkill(payload: { name: string; arguments: Record<string, unknown> }) {
    return (await axios.post('/api/agent/run', payload)).data
  },

  // ---------- 题库 ----------
  async questions(courseId: string, lessonId?: string): Promise<{ questions: Question[]; total: number }> {
    const params = new URLSearchParams({ course_id: courseId })
    if (lessonId) params.set('lesson_id', lessonId)
    return (await axios.get(`/api/questions?${params.toString()}`)).data
  },
  async createQuestion(payload: QuestionCreatePayload): Promise<Question> {
    return (await axios.post('/api/questions', payload)).data
  },
  async updateQuestion(id: string, payload: QuestionCreatePayload): Promise<Question> {
    return (await axios.put(`/api/questions/${id}`, payload)).data
  },
  async deleteQuestion(id: string): Promise<{ deleted: string }> {
    return (await axios.delete(`/api/questions/${id}`)).data
  },
  async generateQuestionExplanation(id: string): Promise<Question> {
    return (await axios.post(`/api/questions/${id}/generate-explanation`)).data
  },

  // ---------- 发布题目到关卡 ----------
  async publishQuestion(questionId: string, taskId: string, courseLineId: string, publishedBy: string): Promise<{ id: number; ok: boolean }> {
    return (await axios.post('/api/teacher/questions/publish', { questionId, taskId, courseLineId, publishedBy })).data
  },

  async unpublishQuestion(questionId: string, taskId: string): Promise<{ ok: boolean }> {
    return (await axios.delete('/api/teacher/questions/unpublish', { data: { questionId, taskId } })).data
  },

  async publishedQuestions(taskId: string): Promise<{ questions: Question[]; total: number }> {
    return (await axios.get(`/api/published-questions/${taskId}`)).data
  },

  async publishedByCourse(courseLineId: string): Promise<{ tasks: Array<{ taskId: string; questions: Question[] }> }> {
    return (await axios.get(`/api/published-questions/course/${courseLineId}`)).data
  },

  // ---------- 引导模式 ----------
  async guidedStart(payload: {
    courseLineId: string
    moduleId: string
    taskId: string
    studentId: string
    studentInput: string
    questionId?: string
    codeDraft?: string
  }): Promise<{
    sessionId: string
    intent: string
    steps: Array<{ title: string; goal: string; knowledge_points: string[] }>
    currentStep: number
    totalSteps: number
    currentStepTitle?: string
    message: string
    citations: Citation[]
    status: string
  }> {
    return (await axios.post('/api/guided/start', payload)).data
  },
  async streamGuidedStart(
    payload: {
      courseLineId: string
      moduleId: string
      taskId: string
      studentId: string
      studentInput: string
      questionId?: string
      codeDraft?: string
    },
    handlers: GuidedStreamHandlers,
  ) {
    await streamSse('/api/guided/start/stream', payload, handlers)
  },
  async guidedMessage(payload: {
    sessionId: string
    studentId: string
    message: string
    codeDraft?: string
  }): Promise<{
    sessionId: string
    currentStep: number
    totalSteps: number
    currentStepTitle?: string
    message: string
    citations: Citation[]
    status: string
  }> {
    return (await axios.post('/api/guided/message', payload)).data
  },
  async streamGuidedMessage(
    payload: {
      sessionId: string
      studentId: string
      message: string
      codeDraft?: string
    },
    handlers: GuidedStreamHandlers,
  ) {
    await streamSse('/api/guided/message/stream', payload, handlers)
  },

  // ---------- 知识库管理 ----------
  async kbFiles(courseLineId?: string): Promise<{ files: Array<{ id: string; filename: string; file_type: string; course_line_id: string | null; chunk_count: number; created_at: string }>; total: number }> {
    const params = courseLineId ? `?course_line_id=${courseLineId}` : ''
    return (await axios.get(`/api/teacher/kb/files${params}`)).data
  },
  async kbDeleteFile(fileId: string): Promise<{ deleted: string }> {
    return (await axios.delete(`/api/teacher/kb/files/${fileId}`)).data
  },
  async kbAssociate(fileId: string, taskId: string): Promise<{ ok: boolean }> {
    return (await axios.post('/api/teacher/kb/associate', { file_id: fileId, task_id: taskId })).data
  },
  async kbDissociate(fileId: string, taskId: string): Promise<{ ok: boolean }> {
    return (await axios.delete('/api/teacher/kb/associate', { data: { file_id: fileId, task_id: taskId } })).data
  },
  async kbTaskFiles(taskId: string): Promise<{ task_id: string; files: Array<{ id: string; filename: string }> }> {
    return (await axios.get(`/api/teacher/kb/task-files/${taskId}`)).data
  },

  // ---------- AI 配置 ----------
  async aiConfig(): Promise<{
    apiKey: string
    apiKeyMasked: string
    baseUrl: string
    model: string
    live: boolean
    timeout: number
  }> {
    return (await axios.get('/api/ai/config')).data
  },
  async updateAiConfig(payload: {
    apiKey?: string
    baseUrl?: string
    model?: string
    live?: boolean
    timeout?: number
  }): Promise<{
    apiKey: string
    apiKeyMasked: string
    baseUrl: string
    model: string
    live: boolean
    timeout: number
  }> {
    return (await axios.put('/api/ai/config', payload)).data
  },
  async aiPresets(): Promise<{ presets: Array<{ name: string; baseUrl: string; model: string; description: string }> }> {
    return (await axios.get('/api/ai/presets')).data
  },
  async testAiConnection(): Promise<{ ok: boolean; message: string; response?: string }> {
    return (await axios.post('/api/ai/test')).data
  },

  // ---------- 教师 AI 分析 ----------
  async analyzeStudent(studentId: string): Promise<{
    studentName: string
    strengths: string[]
    weaknesses: string[]
    improvementPlan: string[]
    recommendedTasks: string[]
    summary: string
  }> {
    return (await axios.post('/api/teacher/ai/analyze-student', { studentId })).data
  },

  async analyzeClass(classId: string): Promise<{
    className: string
    commonWeaknesses: string[]
    topStudents: Array<{ id: string; name: string; score: number }>
    strugglingStudents: Array<{ id: string; name: string; issues: string[] }>
    recommendations: string[]
    summary: string
  }> {
    return (await axios.post('/api/teacher/ai/analyze-class', { classId })).data
  },

  async sendFeedback(teacherId: string, studentId: string, content: string, analysis?: any): Promise<{ id: number; ok: boolean }> {
    return (await axios.post('/api/teacher/feedback/send', { teacherId, studentId, content, analysis })).data
  },

  async getStudentFeedback(studentId: string): Promise<{
    feedback: Array<{
      id: number
      teacher_id: string
      student_id: string
      teacher_name: string
      content: string
      analysis?: any
      created_at: string
    }>
  }> {
    return (await axios.get(`/api/student/feedback/${studentId}`)).data
  },

  async getAllFeedback(): Promise<{
    feedback: Array<{
      id: number
      teacher_id: string
      student_id: string
      teacher_name: string
      student_name: string
      student_no: string
      content: string
      analysis?: any
      created_at: string
    }>
  }> {
    return (await axios.get('/api/teacher/feedback/all')).data
  },

  // Error Book
  async errorBook(studentId: string, status?: string) {
    const params = status ? '?status=' + status : ''
    return (await axios.get('/api/error-book/' + studentId + params)).data
  },
  async errorBookStats(studentId: string) {
    return (await axios.get('/api/error-book/' + studentId + '/stats')).data
  },
  async addErrorEntry(payload: any) {
    return (await axios.post('/api/error-book', payload)).data
  },
  async updateErrorEntry(entryId: number, payload: any) {
    return (await axios.put('/api/error-book/' + entryId, payload)).data
  },
  async deleteErrorEntry(entryId: number) {
    return (await axios.delete('/api/error-book/' + entryId)).data
  },
  async analyzeError(eid: number) {
    return (await axios.post('/api/error-book/' + eid + '/analyze')).data
  },
  async generateVariant(eid: number) {
    return (await axios.post('/api/error-book/' + eid + '/generate-variant')).data
  },
}

interface GuidedStreamHandlers {
  onStatus?: (data: any) => void
  onMetadata?: (data: any) => void
  onDelta?: (text: string) => void
  onDone?: (data: any) => void
  onError?: (data: any) => void
}

async function streamSse(url: string, payload: Record<string, unknown>, handlers: GuidedStreamHandlers) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify(payload),
  })
  if (!response.ok || !response.body) {
    const text = await response.text().catch(() => '')
    throw new Error(text || `stream request failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''
    for (const eventText of events) {
      const parsed = parseSseEvent(eventText)
      if (!parsed) continue
      if (parsed.event === 'status') handlers.onStatus?.(parsed.data)
      if (parsed.event === 'metadata') handlers.onMetadata?.(parsed.data)
      if (parsed.event === 'delta') handlers.onDelta?.(parsed.data.text || '')
      if (parsed.event === 'done') handlers.onDone?.(parsed.data)
      if (parsed.event === 'error') handlers.onError?.(parsed.data)
    }
  }
}

function parseSseEvent(raw: string) {
  const lines = raw.split('\n')
  const event = lines.find((line) => line.startsWith('event:'))?.replace('event:', '').trim()
  const dataLine = lines.find((line) => line.startsWith('data:'))?.replace('data:', '').trim()
  if (!event || !dataLine) return null
  try {
    return { event, data: JSON.parse(dataLine) }
  } catch {
    return null
  }
}
