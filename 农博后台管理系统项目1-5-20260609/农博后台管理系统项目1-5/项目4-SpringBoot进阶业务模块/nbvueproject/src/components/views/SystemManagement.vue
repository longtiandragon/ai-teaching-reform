<template>
  <div class="system-management">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Setting /></el-icon>
        <span class="header-title">系统管理</span>
      </div>
    </div>

    <!-- 顶部装饰区域 -->
    <div class="page-decoration">
      <div class="wheat-left"></div>
      <div class="wheat-right"></div>
      <div class="sun-icon">☀</div>
    </div>

    <!-- 顶部导航标签 -->
    <div class="top-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 用户管理 -->
    <div v-show="activeTab === 'user'" class="content-wrapper">
      <div class="search-section">
        <el-input
          v-model="userQuery.username"
          placeholder="请输入用户名"
          clearable
          class="search-input"
          @keyup.enter="searchUsers"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select 
          v-model="userQuery.status" 
          placeholder="筛选状态 "
          clearable
          class="filter-select"
        >
          <el-option label="正常" :value="0" />
          <el-option label="停用" :value="1" />
        </el-select>

        <el-button type="success" class="btn-recommend" @click="searchUsers">
          搜索
        </el-button>
        <el-button class="btn-reset" @click="resetUserQuery">
          重置
        </el-button>
        
        <el-button type="success" class="btn-add" @click="handleAddUser">
          + 新增用户
        </el-button>
      </div>

      <el-table :data="userList" border class="agri-table" v-loading="userLoading">
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="username" label="用户名" width="150" align="center" />
        <el-table-column prop="nickname" label="昵称" width="150" align="center" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phonenumber" label="手机号码" width="150" align="center" />
        <el-table-column label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 0 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 0 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="200" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" align="center">
          <template #default="scope">
            <div class="action-btns">
              <el-button type="primary" size="small" @click="handleEditUser(scope.row)" plain>查看</el-button>
              <el-button type="danger" size="small" @click="handleDeleteUser(scope.row)" plain>删除</el-button>
              <el-button type="warning" size="small" @click="handleResetPassword(scope.row)" plain>重置密码</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 角色管理 -->
    <div v-show="activeTab === 'role'" class="content-wrapper">
      <div class="search-section">
        <el-input
          v-model="roleQuery.roleName"
          placeholder="请输入角色名称"
          clearable
          class="search-input"
          @keyup.enter="searchRoles"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-button type="success" class="btn-recommend" @click="searchRoles">
          搜索
        </el-button>
        <el-button class="btn-reset" @click="resetRoleQuery">
          重置
        </el-button>
        
        <el-button type="success" class="btn-add" @click="handleAddRole">
          + 新增角色
        </el-button>
      </div>

      <el-table :data="roleList" border class="agri-table role-table" v-loading="roleLoading">
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="roleName" label="角色名称" min-width="220" align="center" />
        <el-table-column prop="roleKey" label="权限字符" min-width="220" align="center" />
        <el-table-column prop="roleSort" label="显示顺序" min-width="160" align="center" />
        <el-table-column label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 0 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 0 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" min-width="220" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" align="center">
          <template #default="scope">
            <div class="action-btns">
              <el-button type="primary" size="small" @click="handleEditRole(scope.row)" plain>查看</el-button>
              <el-button type="danger" size="small" @click="handleDeleteRole(scope.row)" plain>删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 系统配置 -->
    <div v-show="activeTab === 'config'" class="content-wrapper">
      <div class="config-content">
        <el-form :model="systemConfig" label-width="180px" class="config-form">
          <div class="config-section">
            <h3 class="section-title">基础配置</h3>
            <el-form-item label="系统名称">
              <el-input v-model="systemConfig.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="systemConfig.systemVersion" placeholder="请输入系统版本" />
            </el-form-item>
            <el-form-item label="系统LOGO">
              <el-input v-model="systemConfig.systemLogo" placeholder="请输入LOGO地址" />
            </el-form-item>
            <el-form-item label="备案号">
              <el-input v-model="systemConfig.recordNumber" placeholder="请输入备案号" />
            </el-form-item>
          </div>

          <div class="config-section">
            <h3 class="section-title">安全配置</h3>
            <el-form-item label="密码最小长度">
              <el-input-number v-model="systemConfig.passwordMinLength" :min="6" :max="20" />
            </el-form-item>
            <el-form-item label="登录失败锁定次数">
              <el-input-number v-model="systemConfig.loginFailLimit" :min="3" :max="10" />
            </el-form-item>
            <el-form-item label="会话超时时间(分钟)">
              <el-input-number v-model="systemConfig.sessionTimeout" :min="10" :max="120" />
            </el-form-item>
          </div>

          <el-form-item class="form-buttons">
            <el-button type="success" size="large" @click="saveSystemConfig">
              保存配置
            </el-button>
            <el-button size="large" @click="resetSystemConfig">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 用户对话框-->
    <el-dialog 
      v-model="userDialogVisible" 
      :title="userDialogTitle" 
      width="600px"
      class="modern-dialog"
    >
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名 required">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码" required v-if="!isEditUser">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码 show-password" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号码">
          <el-input v-model="userForm.phonenumber" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="userForm.status">
            <el-radio :label="0">正常</el-radio>
            <el-radio :label="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUserForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 角色对话框-->
    <el-dialog 
      v-model="roleDialogVisible" 
      :title="roleDialogTitle" 
      width="600px"
      class="modern-dialog"
    >
      <el-form :model="roleForm" label-width="100px">
        <el-form-item label="角色名称" required>
          <el-input v-model="roleForm.roleName" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="权限字符" required>
          <el-input v-model="roleForm.roleKey" placeholder="请输入权限字符" />
        </el-form-item>
        <el-form-item label="显示顺序">
          <el-input-number v-model="roleForm.roleSort" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="roleForm.status">
            <el-radio :label="0">正常</el-radio>
            <el-radio :label="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="roleForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRoleForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Setting, Lock, Select, RefreshLeft } from '@element-plus/icons-vue'
import request from '../../utils/request'

const activeTab = ref('user')
const userLoading = ref(false)
const roleLoading = ref(false)
const userDialogVisible = ref(false)
const roleDialogVisible = ref(false)
const userDialogTitle = ref('')
const roleDialogTitle = ref('')
const isEditUser = ref(false)

const tabs = [
  { key: 'user', label: '用户管理' },
  { key: 'role', label: '角色管理' },
  { key: 'config', label: '系统配置' },
]

const userQuery = reactive({
  username: '',
  status: undefined
})

const roleQuery = reactive({
  roleName: ''
})

const userList = ref([])
const roleList = ref([])

// 分页参数
const userPagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
})

const rolePagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
})

const userForm = reactive({
  id: undefined,
  username: '',
  nickname: '',
  password: '',
  email: '',
  phonenumber: '',
  status: 0
})

const roleForm = reactive({
  id: undefined,
  roleName: '',
  roleKey: '',
  roleSort: 0,
  status: 0,
  remark: ''
})

const systemConfig = reactive({
  systemName: '农宝智慧助农管理系统',
  systemVersion: 'V1.0.0',
  systemLogo: '/logo.png',
  recordNumber: '京ICP备2345678号',
  passwordMinLength: 6,
  loginFailLimit: 5,
  sessionTimeout: 30
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr
}

// ==================== 用户管理 ====================

const fetchUserList = async () => {
  userLoading.value = true
  try {
    const params: any = {
      pageNum: userPagination.pageNum,
      pageSize: userPagination.pageSize
    }
    
    if (userQuery.username) {
      params.username = userQuery.username
    }
    if (userQuery.status !== undefined) {
      params.status = userQuery.status
    }
    
    const res: any = await request.get('/api/system/user/list', { params })
    if (res.code === 200) {
      userList.value = res.data.records
      userPagination.total = res.data.total
    } else {
      ElMessage.error(res.message || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    userLoading.value = false
  }
}

const searchUsers = () => {
  userPagination.pageNum = 1
  fetchUserList()
}

const resetUserQuery = () => {
  userQuery.username = ''
  userQuery.status = undefined
  userPagination.pageNum = 1
  fetchUserList()
}

const handleAddUser = () => {
  isEditUser.value = false
  userDialogTitle.value = '新增用户'
  Object.assign(userForm, {
    id: undefined,
    username: '',
    nickname: '',
    password: '',
    email: '',
    phonenumber: '',
    status: 0
  })
  userDialogVisible.value = true
}

const handleEditUser = (row: any) => {
  isEditUser.value = true
  userDialogTitle.value = '修改用户'
  Object.assign(userForm, { ...row, password: '' })
  userDialogVisible.value = true
}

const handleDeleteUser = (row: any) => {
  ElMessageBox.confirm('确定要删除该用户吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.delete(`/api/system/user/${row.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchUserList()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleResetPassword = (row: any) => {
  ElMessageBox.confirm('确定要重置该用户密码吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.put(`/api/system/user/resetPassword/${row.id}`)
      if (res.code === 200) {
        ElMessage.success(res.data)
      } else {
        ElMessage.error(res.message || '重置密码失败')
      }
    } catch (error) {
      console.error('重置密码失败:', error)
      ElMessage.error('重置密码失败')
    }
  }).catch(() => {})
}

const submitUserForm = async () => {
  if (!userForm.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  try {
    let res: any
    if (isEditUser.value) {
      // 修改用户
      res = await request.put('/api/system/user', userForm)
    } else {
      // 新增用户
      if (!userForm.password) {
        ElMessage.warning('请输入密码')
        return
      }
      res = await request.post('/api/system/user', userForm)
    }
    
    if (res.code === 200) {
      ElMessage.success(res.data)
      userDialogVisible.value = false
      fetchUserList()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('操作失败')
  }
}

// ==================== 角色管理 ====================

const fetchRoleList = async () => {
  roleLoading.value = true
  try {
    const params: any = {
      pageNum: rolePagination.pageNum,
      pageSize: rolePagination.pageSize
    }
    
    if (roleQuery.roleName) {
      params.roleName = roleQuery.roleName
    }
    
    const res: any = await request.get('/api/system/role/list', { params })
    if (res.code === 200) {
      roleList.value = res.data.records
      rolePagination.total = res.data.total
    } else {
      ElMessage.error(res.message || '获取角色列表失败')
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
    ElMessage.error('获取角色列表失败')
  } finally {
    roleLoading.value = false
  }
}

const searchRoles = () => {
  rolePagination.pageNum = 1
  fetchRoleList()
}

const resetRoleQuery = () => {
  roleQuery.roleName = ''
  rolePagination.pageNum = 1
  fetchRoleList()
}

const handleAddRole = () => {
  roleDialogTitle.value = '新增角色'
  Object.assign(roleForm, {
    id: undefined,
    roleName: '',
    roleKey: '',
    roleSort: 0,
    status: 0,
    remark: ''
  })
  roleDialogVisible.value = true
}

const handleEditRole = (row: any) => {
  roleDialogTitle.value = '修改角色'
  Object.assign(roleForm, row)
  roleDialogVisible.value = true
}

const handleDeleteRole = (row: any) => {
  ElMessageBox.confirm('确定要删除该角色吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.delete(`/api/system/role/${row.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchRoleList()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      console.error('删除角色失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const submitRoleForm = async () => {
  if (!roleForm.roleName) {
    ElMessage.warning('请输入角色名称')
    return
  }
  if (!roleForm.roleKey) {
    ElMessage.warning('请输入权限字符')
    return
  }
  
  try {
    let res: any
    if (roleForm.id) {
      // 修改角色
      res = await request.put('/api/system/role', roleForm)
    } else {
      // 新增角色
      res = await request.post('/api/system/role', roleForm)
    }
    
    if (res.code === 200) {
      ElMessage.success(res.data)
      roleDialogVisible.value = false
      fetchRoleList()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error('操作失败')
  }
}

// ==================== 系统配置 ====================

const fetchSystemConfig = async () => {
  try {
    const res: any = await request.get('/api/system/config/all')
    if (res.code === 200) {
      const configMap = res.data
      systemConfig.systemName = configMap.systemName || '农宝智慧助农管理系统'
      systemConfig.systemVersion = configMap.systemVersion || 'V1.0.0'
      systemConfig.systemLogo = configMap.systemLogo || '/logo.png'
      systemConfig.recordNumber = configMap.recordNumber || '京ICP备2345678号'
      systemConfig.passwordMinLength = parseInt(configMap.passwordMinLength) || 6
      systemConfig.loginFailLimit = parseInt(configMap.loginFailLimit) || 5
      systemConfig.sessionTimeout = parseInt(configMap.sessionTimeout) || 30
    }
  } catch (error) {
    console.error('获取系统配置失败:', error)
  }
}

const saveSystemConfig = async () => {
  try {
    const configMap = {
      systemName: systemConfig.systemName,
      systemVersion: systemConfig.systemVersion,
      systemLogo: systemConfig.systemLogo,
      recordNumber: systemConfig.recordNumber,
      passwordMinLength: systemConfig.passwordMinLength.toString(),
      loginFailLimit: systemConfig.loginFailLimit.toString(),
      sessionTimeout: systemConfig.sessionTimeout.toString()
    }
    
    const res: any = await request.post('/api/system/config/batch', configMap)
    if (res.code === 200) {
      ElMessage.success('配置保存成功')
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (error) {
    console.error('保存系统配置失败:', error)
    ElMessage.error('保存失败')
  }
}

const resetSystemConfig = () => {
  fetchSystemConfig()
  ElMessage.info('配置已重置')
}

onMounted(() => {
  // 初始化加载数据
  fetchUserList()
  fetchRoleList()
  fetchSystemConfig()
})
</script>

<style scoped>
.system-management {
  padding: 0;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  position: relative;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 40px;
  border-bottom: 1px solid #e8e8e8;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  color: #1890ff;
}

.header-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

/* 顶部装饰区域 */
.page-decoration {
  height: 0;
  background: white;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid #e8e8e8;
}

.wheat-left, .wheat-right {
  position: absolute;
  bottom: 0;
  width: 400px;
  height: 100px;
  background-image: 
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 20px,
      #b8956a 20px,
      #b8956a 25px
    );
  opacity: 0.6;
}

.wheat-left {
  left: 0;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M20,80 Q20,40 15,20 M25,80 Q25,40 20,15 M30,80 Q30,40 25,20" fill="none" stroke="%23b8956a" stroke-width="2"/><ellipse cx="15" cy="25" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/><ellipse cx="15" cy="45" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/><ellipse cx="15" cy="65" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/></svg>');
  background-size: 60px 100px;
  background-repeat: repeat-x;
}

.wheat-right {
  right: 0;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M80,80 Q80,40 85,20 M75,80 Q75,40 80,15 M70,80 Q70,40 75,20" fill="none" stroke="%23b8956a" stroke-width="2"/><ellipse cx="85" cy="25" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/><ellipse cx="85" cy="45" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/><ellipse cx="85" cy="65" rx="8" ry="15" fill="%23d4a574" opacity="0.7"/></svg>');
  background-size: 60px 100px;
  background-repeat: repeat-x;
  transform: scaleX(-1);
}

.sun-icon {
  position: absolute;
  top: 20px;
  right: 50%;
  transform: translateX(50%);
  font-size: 50px;
  animation: sunRotate 20s linear infinite;
}

@keyframes sunRotate {
  0% { transform: translateX(50%) rotate(0deg); }
  100% { transform: translateX(50%) rotate(360deg); }
}

/* 顶部导航标签 */
.top-tabs {
  display: flex;
  gap: 0;
  padding: 0;
  background: #f0f2f5;
}

.tab-item {
  padding: 12px 40px;
  background: #e8dcc8;
  border: 1px solid #e8e8e8;
  border-bottom: none;
  cursor: pointer;
  font-size: 15px;
  color: #666;
  transition: all 0.3s;
  margin-right: -1px;
  position: relative;
  z-index: 1;
}

.tab-item:hover {
  background: #f0e6d6;
  color: #333;
}

.tab-item.active {
  background: #fff;
  color: #333;
  font-weight: 500;
  z-index: 2;
  border-bottom: 1px solid #fff;
  margin-bottom: -1px;
}

/* 内容区域 */
.content-wrapper {
  padding: 30px 40px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-top: none;
  margin: 0;
  min-height: calc(100vh - 140px);
  box-sizing: border-box;
}

/* 搜索区域 */
.search-section {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e8dcc8;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 160px;
}

.btn-recommend {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
  padding: 8px 20px;
}

.btn-recommend:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-reset {
  padding: 8px 20px;
}

.btn-add {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
  padding: 8px 24px;
  margin-left: auto;
}

.btn-add:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

/* 农业主题表格 */
.agri-table {
  width: 100% !important;
}

:deep(.agri-table .el-table__inner-wrapper),
:deep(.agri-table .el-table__header-wrapper),
:deep(.agri-table .el-table__body-wrapper),
:deep(.agri-table table) {
  width: 100% !important;
}

:deep(.agri-table th) {
  background: #1890ff !important;
  color: white !important;
  font-weight: 500;
  font-size: 14px;
  padding: 12px 0;
}

:deep(.agri-table th .cell) {
  color: white;
}

:deep(.agri-table td) {
  padding: 10px 0;
  font-size: 14px;
}

:deep(.agri-table .el-table__row:hover > td) {
  background-color: #f5f5f5 !important;
}

:deep(.agri-table .el-table__border) {
  border-color: #e8dcc8;
}

:deep(.agri-table td), :deep(.agri-table th) {
  border-color: #e8dcc8;
}

/* 配置页面 */
.config-content {
  max-width: 900px;
  margin: 0 auto;
}

.config-section {
  background: #fafaf8;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 24px;
  border: 1px solid #e8e8e8;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #1890ff;
}

.config-form {
  width: 100%;
}

.form-buttons {
  text-align: center;
  margin-top: 30px;
}

.form-buttons .el-button {
  min-width: 120px;
}

/* 对话框样式*/
:deep(.el-dialog__header) {
  background: #1890ff;
  color: white;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #f0e6d6;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-button--success) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--success:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #ddd inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #1890ff inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

/* 操作按钮样式 */
.action-btns {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btns .el-button {
  margin: 0 !important;
  padding: 5px 12px;
  font-size: 13px;
  font-weight: 500;
  min-width: 70px;
}

:deep(.el-button--primary.is-plain) {
  color: #1890ff;
  background: #e6f7ff;
  border-color: #1890ff;
}

:deep(.el-button--primary.is-plain:hover) {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
}

:deep(.el-button--danger.is-plain) {
  color: #f56c6c;
  background: #fef0f0;
  border-color: #f56c6c;
}

:deep(.el-button--danger.is-plain:hover) {
  background: #f56c6c;
  border-color: #f56c6c;
  color: white;
}

:deep(.el-button--warning.is-plain) {
  color: #e6a23c;
  background: #fdf6ec;
  border-color: #e6a23c;
}

:deep(.el-button--warning.is-plain:hover) {
  background: #e6a23c;
  border-color: #e6a23c;
  color: white;
}
</style>
