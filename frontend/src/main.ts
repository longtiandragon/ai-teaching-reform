import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElButton, ElProgress, ElTag } from 'element-plus'
import 'element-plus/theme-chalk/base.css'
import 'element-plus/theme-chalk/el-button.css'
import 'element-plus/theme-chalk/el-progress.css'
import 'element-plus/theme-chalk/el-tag.css'
import 'element-plus/theme-chalk/el-message.css'
import './styles.css'
import App from './App.vue'
import { router } from './router'

createApp(App)
  .use(createPinia())
  .use(router)
  .use(ElButton)
  .use(ElProgress)
  .use(ElTag)
  .mount('#app')
