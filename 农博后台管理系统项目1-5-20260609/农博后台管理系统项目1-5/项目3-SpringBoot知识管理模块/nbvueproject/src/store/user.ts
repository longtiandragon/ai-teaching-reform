import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../utils/request'

export const useUserStore = defineStore('user', () => {
  // 状态
  const username = ref<string>('')
  const isLoggedIn = ref<boolean>(false)
  const token = ref<string>('')
  const userRole = ref<string>('管理员')

  // 计算属性
  const userInfo = computed(() => {
    return isLoggedIn.value ? `${username.value}[${userRole.value}]` : '未登录'
  })

  // ==================== 方式1: API登录 (推荐生产环境) ====================
  /**
   * 通过后端API进行登录验证
   * 支持 Spring Boot 和 SSM 两种后端,只需在 request.ts 中切换配置
   */
  const loginWithAPI = async (user: string, pass: string) => {
    try {
      // 调用后端登录接口
      const res: any = await request.post('/dev-api/yjnb/system/login', {
        username: user,
        password: pass
      })
      
      if (res.code === 200 || res.code === 0) {
        // 登录成功,保存用户信息
        username.value = res.data?.username || user
        token.value = res.data?.token || ''
        userRole.value = res.data?.role || '管理员'
        isLoggedIn.value = true
        
        // 持久化到 localStorage
        localStorage.setItem('user', username.value)
        localStorage.setItem('token', token.value)
        localStorage.setItem('role', userRole.value)
        
        console.log('✅ API登录成功:', username.value)
        return { success: true, message: '登录成功' }
      } else {
        console.error('❌ 登录失败:', res.msg || res.message)
        return { success: false, message: res.msg || res.message || '登录失败' }
      }
    } catch (error: any) {
      console.error('❌ 登录请求异常:', error)
      return { 
        success: false, 
        message: error.response?.data?.msg || '网络错误,请检查后端是否启动' 
      }
    }
  }

  // ==================== 方式2: 本地登录 (适合演示/测试) ====================
  /**
   * 本地验证登录(不调用后端API)
   * 适合演示或后端未启动时使用
   */
  const loginLocal = (user: string, pass: string) => {
    // 硬编码的账号密码验证
    if (user === 'admin' && pass === 'admin123') {
      username.value = user
      isLoggedIn.value = true
      userRole.value = '管理员'
      
      localStorage.setItem('user', user)
      localStorage.setItem('role', userRole.value)
      
      console.log('✅ 本地登录成功:', user)
      return { success: true, message: '登录成功' }
    } else {
      console.error('❌ 用户名或密码错误')
      return { success: false, message: '用户名或密码错误' }
    }
  }

  // ==================== 统一登录入口 ====================
  /**
   * 智能登录:优先尝试API,失败时降级到本地验证
   * 这样即使后端挂了也能继续演示
   */
  const login = async (user: string, pass: string = '') => {
    // 先尝试API登录
    const apiResult = await loginWithAPI(user, pass)
    
    if (apiResult.success) {
      return apiResult
    }
    
    // API失败,降级到本地验证
    console.warn('⚠️ API登录失败,使用本地验证')
    return loginLocal(user, pass)
  }

  // ==================== 退出登录 ====================
  const logout = async () => {
    try {
      // 如果有token,调用后端登出接口
      if (token.value) {
        await request.post('/dev-api/yjnb/system/logout', {
          token: token.value
        }).catch(() => {
          // 后端登出失败不影响前端清理
          console.warn('⚠️ 后端登出失败,继续清理本地数据')
        })
      }
    } finally {
      // 清理前端状态
      username.value = ''
      token.value = ''
      userRole.value = ''
      isLoggedIn.value = false
      
      // 清理 localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      
      console.log('✅ 已退出登录')
    }
  }

  // ==================== 检查登录状态 ====================
  const checkLogin = () => {
    const user = localStorage.getItem('user')
    const savedToken = localStorage.getItem('token')
    const savedRole = localStorage.getItem('role')
    
    if (user) {
      username.value = user
      token.value = savedToken || ''
      userRole.value = savedRole || '管理员'
      isLoggedIn.value = true
      
      console.log('✅ 从本地恢复登录状态:', user)
    }
  }

  return {
    // 状态
    username,
    isLoggedIn,
    token,
    userRole,
    
    // 计算属性
    userInfo,
    
    // 方法
    login,          // 推荐使用:智能登录
    loginWithAPI,   // 强制使用API登录
    loginLocal,     // 强制使用本地登录
    logout,
    checkLogin
  }
})

