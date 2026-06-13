import axios from 'axios'

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
}

export interface LearningRecord {
  id: number
  student_id: string
  class_id?: string | null
  course_id: string
  lesson_id: string
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
  async login(user_id: string): Promise<UserInfo> {
    return (await axios.post('/api/session/login', { user_id })).data
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
  async aiCheck(payload: {
    courseLineId: string
    moduleId: string
    taskId: string
    studentId: string
    artifactType?: string
    studentInput: string
    attachments?: Record<string, unknown>[]
    chatHistory?: Record<string, unknown>[]
  }): Promise<AICheckResult> {
    return (await axios.post('/api/ai/check', payload)).data
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
  async analytics() {
    return (await axios.get('/api/teacher/analytics')).data
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
