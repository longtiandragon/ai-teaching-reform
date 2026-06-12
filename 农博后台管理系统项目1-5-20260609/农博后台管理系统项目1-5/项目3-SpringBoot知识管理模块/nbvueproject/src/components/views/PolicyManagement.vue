<template>
  <div class="policy-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Document /></el-icon>
        <span class="header-title">补贴政策管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增政策</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域-->
    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="searchKeyword"
          placeholder="输入文章标题搜索"
          clearable
          @keyup.enter="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-input
          v-model="searchAuthor"
          placeholder="请输入作者来源"
          clearable
          style="width: 200px; margin-left: 10px;"
          @keyup.enter="handleSearch"
        />

        <el-select 
          v-model="searchPublishStatus" 
          placeholder="发布状态 "
          clearable
          style="width: 120px; margin-left: 10px;"
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
          :type="statusFilter === 'recommend' ? 'success' : 'info'"
          :effect="statusFilter === 'recommend' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByStatus('recommend')"
        >
          推荐
        </el-tag>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      style="width: 100%; margin-top: 20px;"
      border
      stripe
      v-loading="loading"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="title" label="文章标题" width="200" show-overflow-tooltip />
      <el-table-column prop="author" label="作者来源" width="150" align="center" />
      <el-table-column prop="resume" label="摘要" min-width="250" show-overflow-tooltip />
      
      <el-table-column label="发布状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.publishStatus === 1 ? 'success' : 'info'" size="small">
            {{ scope.row.publishStatus === 1 ? '已发布' : '未发布' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="publishTime" label="发布时间" width="180" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.publishTime) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="browseNum" label="浏览数" width="100" align="center" />
      
      <el-table-column label="操作" width="280" align="center" fixed="right">
        <template #default="scope">
          <div class="action-btns">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)" plain>编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)" plain>删除</el-button>
            <el-button 
              :type="scope.row.publishStatus === 1 ? 'warning' : 'success'" 
              size="small" 
              @click="handlePublish(scope.row)"
              plain>
              {{ scope.row.publishStatus === 1 ? '取消发布' : '发布' }}
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
      :page-sizes="[10, 20, 50, 100, 160]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px; justify-content: flex-end;"
    />

    <!-- 新增/编辑对话框-->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '修改补贴政策' : '新增补贴政策'" 
      width="600px"
    >
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="文章标题" required>
          <el-input v-model="dialogForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="作者来源">
          <el-input v-model="dialogForm.author" placeholder="请输入作者来源" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="dialogForm.resume" type="textarea" :rows="2" placeholder="请输入摘要" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="dialogForm.content" type="textarea" :rows="4" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="发布状态">
          <el-radio-group v-model="dialogForm.publishStatus">
            <el-radio :label="1">已发布</el-radio>
            <el-radio :label="0">未发布</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否推荐">
          <el-radio-group v-model="dialogForm.recommend">
            <el-radio :label="1">推荐</el-radio>
            <el-radio :label="0">不推荐</el-radio>
          </el-radio-group>
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
import { Search, Document, Plus, Download, Refresh } from '@element-plus/icons-vue'
import request, { exportCsv } from '../../utils/request'

const searchKeyword = ref('')
const searchAuthor = ref('')
const searchPublishStatus = ref<number | undefined>(undefined)
const loading = ref(false)
const tableData = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const allData = ref<any[]>([])
const statusFilter = ref('all')

const dialogForm = reactive({
  id: '',
  title: '',
  author: '',
  resume: '',
  content: '',
  publishStatus: 0,
  recommend: 0,
  browseNum: 0
})

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request.get('/dev-api/yjnb/policy/list')
    if (res.code === 200) {
      allData.value = res.rows || []
      applyFilters()
    }
  } catch (error) {
    console.error('获取列表失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let filteredData = [...allData.value]
  
  // 状态筛选
  if (statusFilter.value === 'unpublished') {
    filteredData = filteredData.filter(item => item.publishStatus === 0)
  } else if (statusFilter.value === 'recommend') {
    filteredData = filteredData.filter(item => item.recommend === 1)
  }
  
  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.title && item.title.toLowerCase().includes(keyword))
    )
  }
  
  if (searchAuthor.value.trim()) {
    const author = searchAuthor.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.author && item.author.toLowerCase().includes(author))
    )
  }
  
  if (searchPublishStatus.value !== undefined) {
    filteredData = filteredData.filter(item => item.publishStatus === searchPublishStatus.value)
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
  searchAuthor.value = ''
  searchPublishStatus.value = undefined
  statusFilter.value = 'all'
  currentPage.value = 1
  applyFilters()
}

const filterByStatus = (status: string) => {
  statusFilter.value = status
  currentPage.value = 1
  applyFilters()
}

const handleExport = () => {
  exportCsv('补贴政策列表', [
    { title: '文章标题', key: 'title' },
    { title: '作者来源', key: 'author' },
    { title: '摘要', key: 'resume' },
    { title: '发布状态', key: 'publishStatus' },
    { title: '发布时间', key: 'publishTime' },
    { title: '浏览数', key: 'browseNum' },
  ], tableData.value)
  ElMessage.success('导出成功')
}

const resetForm = () => {
  dialogForm.id = ''
  dialogForm.title = ''
  dialogForm.author = ''
  dialogForm.resume = ''
  dialogForm.content = ''
  dialogForm.publishStatus = 0
  dialogForm.recommend = 0
  dialogForm.browseNum = 0
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(dialogForm, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!dialogForm.title) {
    ElMessage.warning('请输入文章标题')
    return
  }

  try {
    let res
    if (isEdit.value) {
      res = await request.put('/dev-api/yjnb/policy', dialogForm)
    } else {
      res = await request.post('/dev-api/yjnb/policy', dialogForm)
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
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该补贴政策吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await request.delete(`/dev-api/yjnb/policy/${row.id}`)
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
  const isPublished = row.publishStatus === 1
  ElMessageBox.confirm(
    isPublished ? '是否取消发布该补贴政题' : '是否发布该补贴政题',
    '系统提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const apiUrl = isPublished 
        ? '/dev-api/yjnb/policy/unreleaseAllowancePolicy'
        : '/dev-api/yjnb/policy/releaseAllowancePolicy'
      
      const res = await request.post(apiUrl, [row.id])
      if (res.code === 200) {
        ElMessage.success(isPublished ? '取消发布成功' : '发布成功')
        fetchList()
      } else {
        ElMessage.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
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
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.policy-management {
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

.filter-input {
  width: 200px;
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
:deep(.el-table) {
  font-size: 14px;
  margin: 0 40px 20px 40px;
  border: 1px solid #e8e8e8;
  width: calc(100% - 80px) !important;
}

:deep(.el-table th) {
  background: #1890ff !important;
  color: white !important;
  font-weight: 500;
}

:deep(.el-table th .cell) {
  color: white;
}

:deep(.el-table td) {
  border-color: #e8dcc8;
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: #f5f5f5 !important;
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

/* 按钮主题色*/
:deep(.el-button--primary) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--primary:hover) {
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
</style>
