<template>
  <div class="loan-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><CreditCard /></el-icon>
        <span class="header-title">信贷管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增信贷</el-button>
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

        <el-button type="primary" @click="handleSearch" style="margin-left: 10px;">搜索</el-button>
      </div>

      <!-- 操作按钮组-->
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">新增</el-button>
        <el-button 
          :type="statusFilter === 'all' ? 'primary' : ''"
          @click="filterByStatus('all')"
        >全部</el-button>
        <el-button 
          :type="statusFilter === 'unpublished' ? 'success' : ''"
          @click="filterByStatus('unpublished')"
        >未发布</el-button>
        <el-button 
          :type="statusFilter === 'recommend' ? 'warning' : ''"
          @click="filterByStatus('recommend')"
        >推荐</el-button>
        <el-button @click="handleExport">批量导出</el-button>
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
      :title="isEdit ? '修改信贷信息' : '新增信贷信息'" 
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
        <el-form-item label="图片链接">
          <el-input v-model="dialogForm.image" placeholder="请输入图片链接" />
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
import { Search, CreditCard, Plus, Download, Refresh } from '@element-plus/icons-vue'
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
  image: '',
  publishStatus: 0,
  recommend: 0,
  browseNum: 0
})

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request.get('/dev-api/yjnb/loan/list')
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

const filterByStatus = (status: string) => {
  statusFilter.value = status
  currentPage.value = 1
  applyFilters()
}

const resetForm = () => {
  dialogForm.id = ''
  dialogForm.title = ''
  dialogForm.author = ''
  dialogForm.resume = ''
  dialogForm.content = ''
  dialogForm.image = ''
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
      res = await request.put('/dev-api/yjnb/loan', dialogForm)
    } else {
      res = await request.post('/dev-api/yjnb/loan', dialogForm)
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
  ElMessageBox.confirm('确定要删除该信贷信息吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await request.delete(`/dev-api/yjnb/loan/${row.id}`)
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
    isPublished ? '是否取消发布该信贷信息' : '是否发布该信贷信息',
    '系统提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const apiUrl = isPublished 
        ? '/dev-api/yjnb/loan/unPublishCreditLoan'
        : '/dev-api/yjnb/loan/publishCreditLoan'
      
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

const handleExport = () => {
  exportCsv('信贷列表', [
    { title: '文章标题', key: 'title' },
    { title: '作者来源', key: 'author' },
    { title: '摘要', key: 'resume' },
    { title: '图片', key: 'image' },
    { title: '发布状态', key: 'publishStatus' },
    { title: '发布时间', key: 'publishTime' },
    { title: '浏览数', key: 'browseNum' },
  ], tableData.value)
  ElMessage.success('导出成功')
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
.loan-management {
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

.search-section {
  background: white;
  padding: 20px;
  margin: 20px 40px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}

.search-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

/* 表格样式 */
:deep(.el-table) {
  font-size: 14px;
  margin: 0 40px 20px 40px;
  border: 1px solid #e8e8e8;
  width: calc(100% - 80px) !important;
  background: white;
  border-radius: 4px;
}

:deep(.el-table th) {
  background: #fafafa !important;
  color: #333 !important;
  font-weight: 600;
}

:deep(.el-table th .cell) {
  color: #333;
}

:deep(.el-table td) {
  border-color: #e8e8e8;
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
