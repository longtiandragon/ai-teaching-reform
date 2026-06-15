<template>
  <!-- 教师端：原始马卡龙 HF 风格 -->
  <div v-if="isTeacher" class="ai-config-panel">
    <section class="page-header">
      <div>
        <p class="eyebrow">AI Configuration</p>
        <h2>AI 助手配置</h2>
        <p>配置 DeepSeek 等大语言模型的连接参数。配置后即可使用 AI 聊天、引导模式和任务验收功能。</p>
      </div>
    </section>

    <!-- ========== 系统状态 ========== -->
    <section class="system-status panel">
      <div class="panel-title">
        <h3>系统状态</h3>
        <span :class="['status-badge', health?.deepseek_live ? 'online' : 'offline']">
          {{ health?.deepseek_live ? '在线' : '离线' }}
        </span>
      </div>
      <div class="status-body">
        <div class="status-row">
          <span class="status-label">资料检索</span>
          <span class="status-value">{{ health?.rag_backend || 'loading' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">知识片段</span>
          <span class="status-value">{{ health?.rag_config?.chunks ?? '--' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">课程覆盖</span>
          <span class="status-value">{{ health?.kbCoverage ?? 0 }}%</span>
        </div>
        <div class="status-row">
          <span class="status-label">助教配置</span>
          <span class="status-value">{{ health?.deepseek_configured ? '已配置' : '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">助教状态</span>
          <span class="status-value">{{ health?.deepseek_live ? '可用' : '未开启' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">模型</span>
          <span class="status-value mono">{{ health?.model || '--' }}</span>
        </div>
      </div>
    </section>

    <section class="config-status panel">
      <div class="panel-title">
        <h3>当前状态</h3>
        <span :class="['status-badge', config.live ? 'online' : 'offline']">
          {{ config.live ? '已启用' : '未启用' }}
        </span>
      </div>
      <div class="status-body">
        <div class="status-row">
          <span class="status-label">API 地址</span>
          <span class="status-value">{{ config.baseUrl || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">模型</span>
          <span class="status-value mono">{{ config.model || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">API Key</span>
          <span class="status-value mono">{{ config.apiKeyMasked || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">超时</span>
          <span class="status-value">{{ config.timeout }} 秒</span>
        </div>
        <div class="status-actions">
          <el-button @click="testConnection" :loading="testing" :type="testResult?.ok ? 'success' : testResult?.ok === false ? 'danger' : 'default'">
            {{ testing ? '测试中...' : testResult?.ok ? '连接正常' : testResult?.ok === false ? '连接失败' : '测试连接' }}
          </el-button>
        </div>
        <div v-if="testResult" :class="['test-result', testResult.ok ? 'ok' : 'fail']">
          {{ testResult.message }}
        </div>
      </div>
    </section>

    <section class="presets-section panel">
      <div class="panel-title">
        <h3>快速配置</h3>
        <span class="muted">选择预置模型一键填充</span>
      </div>
      <div class="presets-grid">
        <button
          v-for="preset in presets"
          :key="preset.name"
          type="button"
          class="preset-card"
          @click="applyPreset(preset)"
        >
          <strong>{{ preset.name }}</strong>
          <small>{{ preset.model }}</small>
          <span>{{ preset.description }}</span>
        </button>
      </div>
    </section>

    <section class="config-form panel">
      <div class="panel-title">
        <h3>手动配置</h3>
      </div>
      <div class="form-body">
        <div class="form-row">
          <div class="form-field">
            <label>API 地址</label>
            <input v-model="form.baseUrl" type="text" placeholder="https://api.deepseek.com" />
          </div>
          <div class="form-field">
            <label>模型 ID</label>
            <input v-model="form.model" type="text" placeholder="deepseek-chat" class="mono" />
          </div>
        </div>
        <div class="form-field">
          <label>API Key</label>
          <div class="key-input">
            <input v-model="form.apiKey" :type="showKey ? 'text' : 'password'" placeholder="sk-..." class="mono" />
            <button type="button" class="key-toggle" @click="showKey = !showKey">
              {{ showKey ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>
        <div class="form-row">
          <div class="form-field">
            <label>超时 (秒)</label>
            <input v-model.number="form.timeout" type="number" min="5" max="120" />
          </div>
          <div class="form-field">
            <label>启用 AI</label>
            <button type="button" :class="['toggle-btn', { active: form.live }]" @click="form.live = !form.live">
              {{ form.live ? '已启用' : '未启用' }}
            </button>
          </div>
        </div>
        <div class="form-actions">
          <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
        </div>
      </div>
    </section>
  </div>

  <!-- 学生端：Liquid Glass 暖奶油风格 -->
  <div v-else class="config-scene">
    <div class="grain-overlay" aria-hidden="true"></div>

    <header class="config-header">
      <span class="eyebrow-tag">
        <span class="tag-dot"></span>
        AI Configuration
      </span>
      <h1 class="config-title">AI 助手配置</h1>
      <p class="config-sub">配置 DeepSeek 大语言模型的连接参数。配置后即可使用 AI 聊天、引导模式和任务验收功能。</p>
    </header>

    <section class="status-card">
      <div class="card-header">
        <h3>当前状态</h3>
        <span :class="['status-dot', config.live ? 'online' : 'offline']">
          {{ config.live ? '已启用' : '未启用' }}
        </span>
      </div>
      <div class="status-rows">
        <div class="status-row">
          <span class="row-label">API 地址</span>
          <span class="row-value">{{ config.baseUrl || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="row-label">模型</span>
          <span class="row-value mono">{{ config.model || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="row-label">API Key</span>
          <span class="row-value mono">{{ config.apiKeyMasked || '未配置' }}</span>
        </div>
        <div class="status-row">
          <span class="row-label">超时</span>
          <span class="row-value">{{ config.timeout }} 秒</span>
        </div>
      </div>
      <div class="card-footer">
        <button type="button" class="test-btn" @click="testConnection" :disabled="testing">
          <span v-if="testing" class="btn-spinner"></span>
          <span v-else class="btn-icon-inner">⚡</span>
          <span>{{ testing ? '测试中...' : testResult?.ok ? '连接正常' : testResult?.ok === false ? '连接失败' : '测试连接' }}</span>
        </button>
        <div v-if="testResult" :class="['test-msg', testResult.ok ? 'ok' : 'fail']">
          {{ testResult.message }}
        </div>
      </div>
    </section>

    <section class="presets-card">
      <div class="card-header">
        <h3>快速配置</h3>
        <span class="card-hint">选择预置模型一键填充</span>
      </div>
      <div class="presets-grid-student">
        <button
          v-for="preset in presets"
          :key="preset.name"
          type="button"
          class="preset-btn"
          @click="applyPreset(preset)"
        >
          <strong>{{ preset.name }}</strong>
          <code>{{ preset.model }}</code>
          <span>{{ preset.description }}</span>
        </button>
      </div>
    </section>

    <section class="form-card">
      <div class="card-header">
        <h3>手动配置</h3>
      </div>
      <div class="form-body-student">
        <div class="form-row-student">
          <div class="form-field-student">
            <label>API 地址</label>
            <input v-model="form.baseUrl" type="text" placeholder="https://api.deepseek.com" />
          </div>
          <div class="form-field-student">
            <label>模型 ID</label>
            <input v-model="form.model" type="text" placeholder="deepseek-chat" class="mono" />
          </div>
        </div>
        <div class="form-field-student">
          <label>API Key</label>
          <div class="key-input">
            <input v-model="form.apiKey" :type="showKey ? 'text' : 'password'" placeholder="sk-..." class="mono" />
            <button type="button" class="key-toggle-student" @click="showKey = !showKey">
              {{ showKey ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>
        <div class="form-row-student">
          <div class="form-field-student">
            <label>超时 (秒)</label>
            <input v-model.number="form.timeout" type="number" min="5" max="120" />
          </div>
          <div class="form-field-student">
            <label>启用 AI</label>
            <button type="button" :class="['toggle-btn-student', { active: form.live }]" @click="form.live = !form.live">
              {{ form.live ? '已启用' : '未启用' }}
            </button>
          </div>
        </div>
        <div class="form-actions-student">
          <button type="button" class="save-btn" @click="saveConfig" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            <span v-else class="btn-icon-inner">✓</span>
            <span>{{ saving ? '保存中...' : '保存配置' }}</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'

const route = useRoute()
const isTeacher = computed(() => route.path.startsWith('/teacher'))

const health = ref<any>(null)

const config = ref({
  apiKey: '',
  apiKeyMasked: '',
  baseUrl: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  live: false,
  timeout: 15,
})

const presets = ref<Array<{ name: string; baseUrl: string; model: string; description: string }>>([])
const showKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref<{ ok: boolean; message: string } | null>(null)

const form = reactive({
  apiKey: '',
  baseUrl: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  timeout: 15,
  live: false,
})

onMounted(async () => {
  await loadConfig()
  await loadPresets()
  try { health.value = await api.health() } catch { /* ignore */ }
})

async function loadConfig() {
  try {
    config.value = await api.aiConfig()
    form.apiKey = ''
    form.baseUrl = config.value.baseUrl
    form.model = config.value.model
    form.timeout = config.value.timeout
    form.live = config.value.live
  } catch { /* ignore */ }
}

async function loadPresets() {
  try {
    const res = await api.aiPresets()
    presets.value = res.presets
  } catch { /* ignore */ }
}

function applyPreset(preset: { baseUrl: string; model: string }) {
  form.baseUrl = preset.baseUrl
  form.model = preset.model
}

async function saveConfig() {
  saving.value = true
  try {
    config.value = await api.updateAiConfig({
      apiKey: form.apiKey,
      baseUrl: form.baseUrl,
      model: form.model,
      timeout: form.timeout,
      live: form.live,
    })
    ElMessage.success('配置已保存')
    testResult.value = null
  } catch (e: any) {
    ElMessage.error(`保存失败: ${e.message}`)
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await api.testAiConnection()
  } catch (e: any) {
    testResult.value = { ok: false, message: e.message }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
/* ══════════════════════════════════════════
   教师端样式（马卡龙 HF 原始风格）
   ══════════════════════════════════════════ */
.ai-config-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.ai-config-panel .page-header h2 {
  margin: 0 0 4px;
  font-size: 22px;
}

.ai-config-panel .page-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.ai-config-panel .status-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-config-panel .status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.ai-config-panel .status-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.ai-config-panel .status-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.ai-config-panel .status-value.mono {
  font-family: monospace;
}

.ai-config-panel .status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 100px;
}

.ai-config-panel .status-badge.online {
  background: var(--accent-tertiary);
  color: #fff;
}

.ai-config-panel .status-badge.offline {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.ai-config-panel .status-actions {
  margin-top: 4px;
}

.ai-config-panel .test-result {
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 8px;
}

.ai-config-panel .test-result.ok {
  background: rgba(125, 211, 168, 0.15);
  color: #16a34a;
}

.ai-config-panel .test-result.fail {
  background: rgba(255, 139, 139, 0.15);
  color: #dc2626;
}

.ai-config-panel .presets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 16px 20px;
}

.ai-config-panel .preset-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.ai-config-panel .preset-card:hover {
  border-color: var(--accent-primary);
  background: var(--bg-secondary);
}

.ai-config-panel .preset-card strong {
  font-size: 14px;
  color: var(--text-primary);
}

.ai-config-panel .preset-card small {
  font-family: monospace;
  font-size: 11px;
  color: var(--accent-primary);
}

.ai-config-panel .preset-card span {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.ai-config-panel .form-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-config-panel .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.ai-config-panel .form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-config-panel .form-field label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.ai-config-panel .form-field input {
  padding: 10px 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  background: var(--bg-card);
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s;
}

.ai-config-panel .form-field input:focus {
  border-color: var(--accent-primary);
}

.ai-config-panel .form-field input.mono {
  font-family: monospace;
}

.ai-config-panel .key-input {
  position: relative;
}

.ai-config-panel .key-input input {
  width: 100%;
  padding-right: 40px;
}

.ai-config-panel .key-toggle {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  font-size: 12px;
}

.ai-config-panel .toggle-btn {
  padding: 10px 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-config-panel .toggle-btn.active {
  border-color: var(--accent-tertiary);
  background: rgba(125, 211, 168, 0.1);
  color: #16a34a;
}

.ai-config-panel .form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

@media (max-width: 640px) {
  .ai-config-panel .form-row,
  .ai-config-panel .presets-grid {
    grid-template-columns: 1fr;
  }
}

/* 系统状态面板 */
.ai-config-panel .system-status .status-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.ai-config-panel .system-status .status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.ai-config-panel .system-status .status-row:last-child {
  border-bottom: none;
}

.ai-config-panel .system-status .status-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.ai-config-panel .system-status .status-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.ai-config-panel .system-status .status-value.mono {
  font-family: monospace;
}

/* ══════════════════════════════════════════
   学生端样式（Liquid Glass 暖奶油）
   ══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.config-scene {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
  position: relative;
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
}

.grain-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  pointer-events: none;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
}

.config-header {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.7s cubic-bezier(0.32, 0.72, 0, 1) 0.05s forwards;
}

.eyebrow-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px 5px 10px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.03);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #78716C;
  margin-bottom: 14px;
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #D97706;
}

.config-title {
  margin: 0 0 8px;
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: #0F172A;
}

.config-sub {
  margin: 0;
  font-size: 14px;
  color: #78716C;
  line-height: 1.6;
}

.status-card,
.presets-card,
.form-card {
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.012);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.status-card {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.12s forwards;
}

.presets-card {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.2s forwards;
}

.form-card {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.6s cubic-bezier(0.32, 0.72, 0, 1) 0.28s forwards;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
}

.card-header h3 {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  color: #0F172A;
}

.card-hint {
  font-size: 12px;
  color: #A8A29E;
}

.status-dot {
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 700;
}

.status-dot.online {
  background: rgba(125, 211, 168, 0.15);
  color: #059669;
}

.status-dot.offline {
  background: rgba(0, 0, 0, 0.04);
  color: #A8A29E;
}

.status-rows {
  padding: 0 24px;
}

.status-rows .status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.status-rows .status-row:last-child {
  border-bottom: none;
}

.row-label {
  font-size: 13px;
  color: #A8A29E;
}

.row-value {
  font-size: 13px;
  font-weight: 500;
  color: #0F172A;
}

.row-value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

.card-footer {
  padding: 16px 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.test-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 100px;
  background: transparent;
  color: #78716C;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  font-family: inherit;
  align-self: flex-start;
}

.test-btn:not(:disabled):hover {
  border-color: rgba(217, 119, 6, 0.2);
  color: #D97706;
}

.test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-inner {
  font-size: 12px;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.test-msg {
  font-size: 12px;
  padding: 8px 14px;
  border-radius: 10px;
  line-height: 1.5;
}

.test-msg.ok {
  background: rgba(125, 211, 168, 0.1);
  color: #059669;
}

.test-msg.fail {
  background: rgba(255, 139, 139, 0.1);
  color: #DC2626;
}

.presets-grid-student {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 0 24px 20px;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.05);
  border-radius: 14px;
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  font-family: inherit;
}

.preset-btn:hover {
  border-color: rgba(217, 119, 6, 0.2);
  background: rgba(217, 119, 6, 0.02);
  transform: translateY(-1px);
}

.preset-btn strong {
  font-size: 14px;
  font-weight: 600;
  color: #0F172A;
}

.preset-btn code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #D97706;
}

.preset-btn span {
  font-size: 12px;
  color: #A8A29E;
  line-height: 1.4;
}

.form-body-student {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-row-student {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-field-student {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field-student label {
  font-size: 12px;
  font-weight: 600;
  color: #78716C;
  letter-spacing: 0.02em;
}

.form-field-student input {
  padding: 11px 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  font-size: 13px;
  font-family: inherit;
  background: transparent;
  color: #0F172A;
  outline: none;
  transition: border-color 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.form-field-student input:focus {
  border-color: #D97706;
}

.form-field-student input.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

.key-toggle-student {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #A8A29E;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 6px;
  font-family: inherit;
}

.key-toggle-student:hover {
  color: #D97706;
}

.toggle-btn-student {
  padding: 11px 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  background: transparent;
  color: #A8A29E;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
  font-family: inherit;
}

.toggle-btn-student.active {
  border-color: rgba(125, 211, 168, 0.3);
  background: rgba(125, 211, 168, 0.08);
  color: #059669;
}

.form-actions-student {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 100px;
  background: #0F172A;
  color: #FFFBEB;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  font-family: inherit;
}

.save-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
}

.save-btn:not(:disabled):active {
  transform: scale(0.98);
}

.save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .form-row-student,
  .presets-grid-student {
    grid-template-columns: 1fr;
  }
}
</style>
