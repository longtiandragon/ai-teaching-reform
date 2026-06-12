import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../utils/request'

export const useUserStore = defineStore('user', () => {
  // 状态
  const username = ref<string>('')
  const isLoggedIn = ref<boolean>(false)
  const token = ref<string>('')

  // 计算属性
  const userInfo = computed(() => {
    return isLoggedIn.value ? `${username.value}[管理员]` : '未登录'
  })

  // 动作 - 调用后端登录接口
  const login = async (user: string, password: string) => {
    try {
      // 调用后端登录接口
      const res: any = await request.post('/dev-api/yjnb/system/login', {
        username: user,
        password: password
      })
      
      if (res.code === 200) {
        username.value = user
        token.value = res.token || ''  // 保存后端返回的 token
        isLoggedIn.value = true
        
        // 保存到 localStorage
        localStorage.setItem('user', user)
        localStorage.setItem('token', token.value)
        
        return { success: true, message: '登录成功' }
      } else {
        return { success: false, message: res.msg || '登录失败' }
      }
    } catch (error: any) {
      console.error('登录失败:', error)
      return { success: false, message: error.message || '登录失败' }
    }
  }

  const logout = async () => {
    try {
      // 可选：调用后端登出接口
      // await request.post('/dev-api/yjnb/system/logout')
      
      username.value = ''
      token.value = ''
      isLoggedIn.value = false
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  const checkLogin = () => {
    const user = localStorage.getItem('user')
    const savedToken = localStorage.getItem('token')
    if (user && savedToken) {
      username.value = user
      token.value = savedToken
      isLoggedIn.value = true
    }
  }

  return {
    username,
    isLoggedIn,
    token,
    userInfo,
    login,
    logout,
    checkLogin
  }
})

