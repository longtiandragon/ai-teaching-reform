<template>
  <div class="advertisement-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Picture /></el-icon>
        <span class="header-title">广告管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增广告</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域-->
    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="searchKeyword"
          placeholder="输入广告标题搜索"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select 
          v-model="searchPosition" 
          placeholder="广告位置" 
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="首页轮播图" value="banner" />
          <el-option label="侧边栏" value="sidebar" />
          <el-option label="弹窗" value="popup" />
          <el-option label="底部" value="footer" />
        </el-select>

        <el-select 
          v-model="searchStatus" 
          placeholder="状态 "
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="已发布" :value="1" />
          <el-option label="未发布" :value="0" />
        </el-select>

        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>

      <!-- 快捷筛选标题-->
      <div class="filter-tags">
        <span class="filter-label">快捷筛选：</span>
        <el-tag
          :type="statusFilter === 'all' ? 'primary' : 'info'"
          :effect="statusFilter === 'all' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByStatus('all')"
        >
          全部
        </el-tag>
        <el-tag
          :type="statusFilter === 'unpublished' ? 'warning' : 'info'"
          :effect="statusFilter === 'unpublished' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByStatus('unpublished')"
        >
          未发布
        </el-tag>
        <el-tag
          :type="statusFilter === 'active' ? 'success' : 'info'"
          :effect="statusFilter === 'active' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByStatus('active')"
        >
          进行中
        </el-tag>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      style="width: 100%;"
      border
      stripe
      v-loading="loading"
      class="modern-table"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="title" label="广告标题" width="180" show-overflow-tooltip />
      
      <el-table-column label="图片" width="120" align="center">
        <template #default="scope">
          <el-image
            v-if="scope.row.image"
            :src="scope.row.image"
            fit="cover"
            style="width: 100px; height: 50px; border-radius: 4px; cursor: pointer;"
            :preview-src-list="[scope.row.image]"
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <span v-else style="color: #ccc; font-size: 12px;">暂无</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="position" label="广告位置" width="120" align="center">
        <template #default="scope">
          <el-tag :type="getPositionType(scope.row.position)" size="small">
            {{ getPositionText(scope.row.position) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="linkUrl" label="链接地址" min-width="200" show-overflow-tooltip />
      
      <el-table-column label="开始时间" width="120" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.startTime) }}
        </template>
      </el-table-column>
      
      <el-table-column label="结束时间" width="120" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.endTime) }}
        </template>
      </el-table-column>
      
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row)" size="small">
            {{ getStatusText(scope.row) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="clickCount" label="点击量" width="100" align="center">
        <template #default="scope">
          <span style="color: #409eff; font-weight: 600;">{{ scope.row.clickCount || 0 }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="280" align="center" fixed="right">
        <template #default="scope">
          <div class="action-btns">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)" plain>编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)" plain>删除</el-button>
            <el-button 
              :type="scope.row.status === 1 ? 'warning' : 'success'" 
              size="small" 
              @click="handlePublish(scope.row)"
              plain>
              {{ scope.row.status === 1 ? '取消发布' : '发布' }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px; justify-content: flex-end;"
    />

    <!-- 新增/编辑对话框-->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '修改广告' : '新增广告'" 
      width="700px"
      class="modern-dialog"
    >
      <el-form :model="dialogForm" label-width="100px" :rules="rules" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="广告标题" prop="title">
              <el-input v-model="dialogForm.title" placeholder="请输入广告标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="广告位置" prop="position">
              <el-select v-model="dialogForm.position" placeholder="请选择" style="width: 100%;">
                <el-option label="首页轮播图" value="banner" />
                <el-option label="侧边栏" value="sidebar" />
                <el-option label="弹窗" value="popup" />
                <el-option label="底部" value="footer" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="广告图片" prop="image">
          <div class="image-upload-container">
            <el-upload
              class="image-uploader"
              :show-file-list="false"
              :auto-upload="false"
              accept="image/*"
              @change="handleImageChange"
            >
              <img v-if="dialogForm.image" :src="dialogForm.image" class="preview-image" />
              <el-icon v-else class="uploader-icon"><Plus /></el-icon>
            </el-upload>
            <div class="upload-tips">
              <p>点击上传广告图片（推荐尺寸：400x200）</p>
              <el-input 
                v-model="dialogForm.image" 
                placeholder="或直接输入图片URL" 
                clearable
                size="small"
                style="margin-top: 8px;"
              />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="链接地址">
          <el-input v-model="dialogForm.linkUrl" placeholder="请输入链接地址" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startTime">
              <el-date-picker
                v-model="dialogForm.startTime"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endTime">
              <el-date-picker
                v-model="dialogForm.endTime"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="dialogForm.sort" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="dialogForm.status">
                <el-radio :label="1">发布</el-radio>
                <el-radio :label="0">不发题</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="dialogForm.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Picture, Download, Refresh } from '@element-plus/icons-vue'
import request, { exportCsv } from '../../utils/request'

const searchKeyword = ref('')
const searchPosition = ref('')
const searchStatus = ref<number | undefined>(undefined)
const loading = ref(false)
const tableData = ref<any[]>([])
const allData = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const statusFilter = ref('all')
const formRef = ref()

const dialogForm = reactive({
  id: undefined,
  title: '',
  image: '',
  position: '',
  linkUrl: '',
  startTime: '',
  endTime: '',
  sort: 0,
  status: 1,
  clickCount: 0,
  remark: ''
})

const rules = {
  title: [{ required: true, message: '广告标题不能为空', trigger: 'blur' }],
  position: [{ required: true, message: '请选择广告位置', trigger: 'change' }],
  image: [{ required: true, message: '请输入图片URL', trigger: 'blur' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
}

// 模拟数据
const mockData = [
  {
    id: 1,
    title: '春季农产品促销活动',
    image: 'https://via.placeholder.com/400x200/409eff/fff?text=广告图片1',
    position: 'banner',
    linkUrl: 'https://example.com/promo',
    startTime: '2025-01-01 00:00:00',
    endTime: '2025-12-31 23:59:59',
    sort: 1,
    status: 1,
    clickCount: 1250,
    remark: '首页主推广告'
  },
  {
    id: 2,
    title: '助农政策宣传',
    image: 'https://via.placeholder.com/400x200/67c23a/fff?text=广告图片2',
    position: 'sidebar',
    linkUrl: 'https://example.com/policy',
    startTime: '2025-01-15 00:00:00',
    endTime: '2025-06-30 23:59:59',
    sort: 2,
    status: 1,
    clickCount: 850,
    remark: '侧边栏政策广告'
  },
  {
    id: 3,
    title: '农贸市场招商',
    image: 'https://via.placeholder.com/400x200/e6a23c/fff?text=广告图片3',
    position: 'popup',
    linkUrl: 'https://example.com/market',
    startTime: '2025-02-01 00:00:00',
    endTime: '2025-03-31 23:59:59',
    sort: 3,
    status: 0,
    clickCount: 0,
    remark: '弹窗广告'
  },
]

const getPositionType = (position: string) => {
  const types: any = {
    'banner': 'danger',
    'sidebar': 'warning',
    'popup': 'success',
    'footer': 'info'
  }
  return types[position] || 'info'
}

const getPositionText = (position: string) => {
  const texts: any = {
    'banner': '首页轮播图',
    'sidebar': '侧边栏',
    'popup': '弹窗',
    'footer': '底部'
  }
  return texts[position] || position
}

const getStatusType = (row: any) => {
  if (row.status === 0) return 'info'
  const now = new Date()
  const start = new Date(row.startTime)
  const end = new Date(row.endTime)
  if (now < start) return 'warning'
  if (now > end) return 'danger'
  return 'success'
}

const getStatusText = (row: any) => {
  if (row.status === 0) return '未发布'
  const now = new Date()
  const start = new Date(row.startTime)
  const end = new Date(row.endTime)
  if (now < start) return '待开始'
  if (now > end) return '已过期'
  return '进行中'
}

// 从数据库加载数据
const fetchList = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/dev-api/yjnb/advertisement/list')
    if (res.code === 200) {
      allData.value = res.rows || []
      console.log('从数据库加载了', allData.value.length, '条广告数据')
      applyFilters()
    }
  } catch (error) {
    console.error('获取列表失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const initData = () => {
  fetchList()
}

const applyFilters = () => {
  let filteredData = [...allData.value]
  
  // 状态筛选
  if (statusFilter.value === 'unpublished') {
    filteredData = filteredData.filter(item => item.status === 0)
  } else if (statusFilter.value === 'active') {
    filteredData = filteredData.filter(item => {
      if (item.status === 0) return false
      const now = new Date()
      const start = new Date(item.startTime)
      const end = new Date(item.endTime)
      return now >= start && now <= end
    })
  }
  
  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.title && item.title.toLowerCase().includes(keyword))
    )
  }
  
  if (searchPosition.value) {
    filteredData = filteredData.filter(item => item.position === searchPosition.value)
  }
  
  if (searchStatus.value !== undefined) {
    filteredData = filteredData.filter(item => item.status === searchStatus.value)
  }
  
  total.value = filteredData.length
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  tableData.value = filteredData.slice(start, end)
}

const handleSearch = () => {
  currentPage.value = 1
  applyFilters()
}

const handleReset = () => {
  searchKeyword.value = ''
  searchPosition.value = ''
  searchStatus.value = undefined
  statusFilter.value = 'all'
  currentPage.value = 1
  applyFilters()
}

const filterByStatus = (status: string) => {
  statusFilter.value = status
  currentPage.value = 1
  applyFilters()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(dialogForm, {
    id: undefined,
    title: '',
    image: '',
    position: '',
    linkUrl: '',
    startTime: '',
    endTime: '',
    sort: 0,
    status: 1,
    clickCount: 0,
    remark: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(dialogForm, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    try {
      let res: any
      // 准备提交的数据
      const submitData = { ...dialogForm }
      // 如果是新增，删除id字段，让后端自动生成
      if (!isEdit.value) {
        delete submitData.id
      }
      
      if (isEdit.value) {
        res = await request.put('/dev-api/yjnb/advertisement', submitData)
      } else {
        res = await request.post('/dev-api/yjnb/advertisement', submitData)
      }
      
      if (res.code === 200) {
        ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
        dialogVisible.value = false
        fetchList()
      } else {
        ElMessage.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该广告吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.delete(`/dev-api/yjnb/advertisement/${row.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchList()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handlePublish = (row: any) => {
  const action = row.status === 1 ? '取消发布' : '发布'
  ElMessageBox.confirm(`确定要${action}该广告吗？`, '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      let res: any
      if (row.status === 1) {
        res = await request.post('/dev-api/yjnb/advertisement/unpublish', [row.id])
      } else {
        res = await request.post('/dev-api/yjnb/advertisement/publish', [row.id])
      }
      if (res.code === 200) {
        ElMessage.success(`${action}成功`)
        fetchList()
      } else {
        ElMessage.error(res.msg || `${action}失败`)
      }
    } catch (error) {
      console.error(`${action}失败:`, error)
      ElMessage.error(`${action}失败`)
    }
  }).catch(() => {})
}

const handleExport = () => {
  exportCsv('广告列表', [
    { title: '广告标题', key: 'title' },
    { title: '图片', key: 'image' },
    { title: '位置', key: 'position' },
    { title: '链接', key: 'linkUrl' },
    { title: '开始时间', key: 'startTime' },
    { title: '结束时间', key: 'endTime' },
    { title: '排序', key: 'sort' },
    { title: '状态', key: 'status' },
    { title: '点击量', key: 'clickCount' },
  ], tableData.value)
  ElMessage.success('导出成功')
}

const handleImageChange = (file: any) => {
  const reader = new FileReader()
  reader.onload = (e: any) => {
    dialogForm.image = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  applyFilters()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  applyFilters()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr.substring(0, 10)
}

onMounted(() => {
  initData()
})
</script>

<style scoped>
.advertisement-management {
  width: 100%;
  padding: 0;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 40px;
  border-bottom: 1px solid #e8e8e8;
  position: relative;
  overflow: hidden;
}





.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1;
}

.header-icon {
  font-size: 24px;
  color: #1890ff;
}

.header-title {
  font-size: 22px;
  font-weight: 600;
  color: #5a4a3a;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  gap: 12px;
  z-index: 1;
}

.header-right .el-button {
  border: none;
  font-weight: 500;
}

/* 搜索筛选区域*/
.search-section {
  background: white;
  padding: 20px;
  margin: 20px 40px;
  border-radius: 0;
  border: 1px solid #e8e8e8;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  width: 320px;
}

.filter-select {
  width: 150px;
}

/* 快捷筛选标题*/
.filter-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8dcc8;
}

.filter-label {
  font-size: 14px;
  color: #8b7355;
  font-weight: 500;
}

.filter-tag {
  cursor: pointer;
  user-select: none;
  transition: all 0.3s;
  font-size: 13px;
  padding: 6px 16px;
  border-color: #e8e8e8;
}

.filter-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(133, 185, 70, 0.2);
}

/* 表格样式 */
.modern-table {
  margin: 0 40px 20px 40px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  width: calc(100% - 80px) !important;
}

:deep(.modern-table th) {
  background: #1890ff !important;
  color: white !important;
  font-weight: 500;
  font-size: 14px;
  padding: 12px 0;
}

:deep(.modern-table th .cell) {
  color: white;
}

:deep(.modern-table td) {
  padding: 10px 0;
  border-color: #e8dcc8;
}

:deep(.modern-table__row:hover > td) {
  background-color: #f5f5f5 !important;
}

:deep(.modern-table td), :deep(.modern-table th) {
  border-color: #e8dcc8;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 24px;
}

.modern-dialog :deep(.el-dialog__header) {
  background: #1890ff;
  padding: 20px;
}

.modern-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.modern-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.image-upload-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.image-uploader {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 200px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.image-uploader:hover {
  border-color: #409eff;
  background: #e6f7ff;
}

.preview-image {
  width: 200px;
  height: 120px;
  object-fit: cover;
  display: block;
}

.uploader-icon {
  font-size: 32px;
  color: #8c939d;
}

.upload-tips {
  flex: 1;
}

.upload-tips p {
  margin: 0 0 8px;
  color: #606266;
  font-size: 14px;
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

/* 按钮样式覆盖 */
:deep(.el-button--primary) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--primary:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
}

:deep(.el-button--success) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--success:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
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

:deep(.el-button--success.is-plain) {
  color: #1890ff;
  background: #e6f7ff;
  border-color: #1890ff;
}

:deep(.el-button--success.is-plain:hover) {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #1890ff inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

:deep(.el-select .el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

/* 分页样式 */
:deep(.el-pagination) {
  justify-content: center;
  padding: 20px 0;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #1890ff;
  border-color: #1890ff;
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: #1890ff;
}
</style>
