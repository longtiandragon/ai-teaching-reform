import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/css/reset.css'
import router from './router/router.ts'	// 导入路由模块
import pinia from './store'	// 导入 Pinia
import App from './components/Blank.vue'
import Menu from './components/Menu.vue'
import NavHeader from './components/NavHeader.vue'

// import './mock/mockServer.ts'  // 已禁用Mock，使用真实后端接口


const app = createApp(App)

app.component('nav-header', NavHeader)
     .component('side-menu', Menu)

app.use(router).use(ElementPlus).use(pinia);
app.mount('#app')





