import { createRouter, createWebHistory} from 'vue-router'
import login from '../login.vue'
import Main from '../components/Main.vue'
import Konwladge from '../components/views/Konwladge.vue'
import DataDashboard from '../components/views/DataDashboard.vue'
import ProduceManagement from '../components/views/ProduceManagement.vue'
import MarketManagement from '../components/views/MarketManagement.vue'
import LoanManagement from '../components/views/LoanManagement.vue'
import PolicyManagement from '../components/views/PolicyManagement.vue'
import SystemManagement from '../components/views/SystemManagement.vue'
import AdvertisementManagement from '../components/views/AdvertisementManagement.vue'
import ServiceManagement from '../components/views/ServiceManagement.vue'

const routesObj = [
    {
      path: '/',
      redirect:'/login' // 当用户访问根路径时，重定向到登录页
    },
    {
      path: '/login',
      name: 'login',
      component: login 
    },
    {
        path: '/main',
        name: 'Main',
        component: Main,
        children:[
          {  
            path:'konwladge/index',
            name:"konwladeg",
            component:Konwladge
          },
          {
            path:'dashboard',
            name:"dashboard",
            component:DataDashboard
          },
          {
            path:'produce',
            name:"produce",
            component:ProduceManagement
          },
          {
            path:'market',
            name:"market",
            component:MarketManagement
          },
          {
            path:'loan',
            name:"loan",
            component:LoanManagement
          },
          {
            path:'policy',
            name:"policy",
            component:PolicyManagement
          },
          {
            path:'system',
            name:"system",
            component:SystemManagement
          },
          {
            path:'advertisement',
            name:"advertisement",
            component:AdvertisementManagement
          },
          {
            path:'service',
            name:"service",
            component:ServiceManagement
          }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routesObj // 定义了路由对象数组
});


router.beforeEach((to, from, next) => {
    if (to.path === "/login") {// 使用===检查目标路径是否为/login
        next(); // 如果是，则允许继续导航
    } else if (to.path === '/main') { // 使用===检查目标路径是否为/main
        if (localStorage.getItem("user") !== null) {
            next(); // 如果用户已登录（localStorage中有"user"），则允许访问
        } else {
            next('/login'); // 否则重定向到登录页
        } 
    } else {
        next(); // 对于其他所有路由，默认放行
    }
});

export default router;