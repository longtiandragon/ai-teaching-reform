import { defineStore } from 'pinia'
import { api, type AgentSkill, type Course, type CourseLine, type LearningMap, type LearningTaskDetail, type Lesson } from '../api'

const DEFAULT_COURSE_ID = 'springboot-course-12'

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [] as Course[],
    activeCourseId: DEFAULT_COURSE_ID,
    activeLessonId: '',
    lesson: null as Lesson | null,
    courseLines: [] as CourseLine[],
    learningMap: null as LearningMap | null,
    activeTaskId: '',
    task: null as LearningTaskDetail | null,
    skills: [] as AgentSkill[],
    health: null as Record<string, any> | null,
  }),
  getters: {
    course: (state) => state.courses.find((course) => course.id === state.activeCourseId) || state.courses[0],
  },
  actions: {
    async load() {
      const [health, courses, skills, courseLines] = await Promise.all([api.health(), api.courses(), api.skills(), api.courseLines()])
      this.health = health
      this.courses = courses
      this.courseLines = courseLines
      if (!this.courses.some((course) => course.id === this.activeCourseId)) {
        this.activeCourseId = this.courses[0]?.id || DEFAULT_COURSE_ID
      }
      const currentCourse = this.courses.find((course) => course.id === this.activeCourseId) || this.courses[0]
      if (!currentCourse?.lessons.some((lesson) => lesson.id === this.activeLessonId)) {
        this.activeLessonId = currentCourse?.lessons[0]?.id || ''
      }
      if (this.activeCourseId && this.activeLessonId) {
        await this.loadLesson(this.activeLessonId)
      }
    },
    async setCourse(courseId: string) {
      if (courseId === this.activeCourseId) return
      this.activeCourseId = courseId
      const course = this.courses.find((item) => item.id === courseId)
      this.activeLessonId = course?.lessons[0]?.id || ''
      this.lesson = null
      if (this.activeLessonId) {
        await this.loadLesson(this.activeLessonId)
      }
      this.learningMap = null
      this.activeTaskId = ''
      this.task = null
    },
    async loadLesson(lessonId: string) {
      if (!lessonId) return
      this.activeLessonId = lessonId
      this.lesson = await api.lesson(this.activeCourseId, lessonId)
    },
    async loadLearningMap(studentId?: string) {
      this.learningMap = await api.learningMap(this.activeCourseId, studentId)
      const activeTask = this.learningMap.tasks.find((task) => task.status === 'active')
        || this.learningMap.tasks.find((task) => task.status === 'needs_revision')
        || this.learningMap.tasks[0]
      if (activeTask && !this.activeTaskId) {
        await this.loadTask(activeTask.id)
      }
    },
    async loadTask(taskId: string) {
      this.activeTaskId = taskId
      this.task = await api.learningTask(taskId)
    },
  },
})
