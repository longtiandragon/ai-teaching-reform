<template>
  <div class="expert-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><User /></el-icon>
        <span class="header-title">专家列表</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增专家</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域-->
    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="queryParams.title"
          placeholder="输入专家名称/专家简介搜题"
          clearable
          class="search-input"
          @keyup.enter="handleQuery"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-input
          v-model="queryParams.resume"
          placeholder="请输入专家简介"
          clearable
          class="filter-input"
          @keyup.enter="handleQuery"
        />

        <el-select 
          v-model="queryParams.field" 
          placeholder="专家领域" 
          clearable
          class="filter-select"
          @change="handleQuery"
        >
          <el-option label="农业技术" value="农业技术" />
          <el-option label="种植技术" value="种植技术" />
          <el-option label="养殖技术" value="养殖技术" />
          <el-option label="农产品加题" value="农产品加题" />
        </el-select>

        <el-select 
          v-model="queryParams.level" 
          placeholder="专家职称" 
          clearable
          class="filter-select"
          @change="handleQuery"
        >
          <el-option label="教授" value="教授" />
          <el-option label="副教授" value="副教授" />
          <el-option label="研究员" value="研究员" />
          <el-option label="高级农艺师" value="高级农艺师" />
        </el-select>

        <el-button type="primary" :icon="Search" @click="handleQuery">搜索</el-button>
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
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      border
      stripe
      v-loading="loading"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="name" label="专家姓名" width="120" show-overflow-tooltip />
      
      <el-table-column label="照片" width="100" align="center">
        <template #default="scope">
          <el-image
            v-if="scope.row.image"
            :src="scope.row.image"
            fit="cover"
            style="width: 60px; height: 60px; border-radius: 4px; cursor: pointer;"
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
      
      <el-table-column prop="catgory" label="头衔" width="140" align="center" />
      <el-table-column prop="resume" label="专家简介" min-width="200" show-overflow-tooltip />
      <el-table-column prop="author" label="所属院题" width="150" align="center" />
      <el-table-column prop="field" label="专家领域" width="120" align="center" />
      
      <el-table-column prop="publishTime" label="发布时间" width="180" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.publishTime) }}
        </template>
      </el-table-column>

      <el-table-column label="发布状态" width="130" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.publishStatus"
            :active-value="1"
            :inactive-value="0"
            active-text="已发布"
            inactive-text="未发布"
            inline-prompt
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>

      <el-table-column prop="browseNum" label="浏览数" width="100" align="center" />
      
      <el-table-column label="操作" width="180" align="center" fixed="right">
        <template #default="scope">
          <div class="action-btns">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)" plain>编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)" plain>删除</el-button>
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
      :title="isEdit ? '修改专家信息' : '新增专家信息'" 
      width="600px"
    >
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="专家姓名" required>
          <el-input v-model="dialogForm.name" placeholder="请输入专家姓名" />
        </el-form-item>
        <el-form-item label="专家照片">
          <div class="image-upload-container">
            <el-upload
              class="image-uploader"
              :show-file-list="false"
              :auto-upload="false"
              accept="image/*"
              @change="handleImageChange"
            >
              <img v-if="dialogForm.avatar" :src="dialogForm.avatar" class="preview-image" />
              <el-icon v-else class="uploader-icon"><Plus /></el-icon>
            </el-upload>
              <div class="upload-tips">
                <p>点击上传专家照片（推荐正方形）</p>
              <el-input 
                v-model="dialogForm.avatar" 
                placeholder="或直接输入图片URL" 
                clearable
                size="small"
                style="margin-top: 8px;"
              />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="专家简介">
          <el-input v-model="dialogForm.introduction" type="textarea" :rows="2" placeholder="请输入专家简介" />
        </el-form-item>
        <el-form-item label="职称">
          <el-input v-model="dialogForm.title" placeholder="请输入专家职称" />
        </el-form-item>
        <el-form-item label="所属机构">
          <el-input v-model="dialogForm.organization" placeholder="请输入所属机构" />
        </el-form-item>
        <el-form-item label="专业领域">
          <el-select v-model="dialogForm.specialty" placeholder="请选择专业领域" style="width: 100%;">
            <el-option label="农业技术" value="农业技术" />
            <el-option label="种植技术" value="种植技术" />
            <el-option label="养殖技术" value="养殖技术" />
            <el-option label="农产品加题" value="农产品加题" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布状态">
          <el-radio-group v-model="dialogForm.status">
            <el-radio :label="1">已发布</el-radio>
            <el-radio :label="0">未发布</el-radio>
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
import { Search, Picture, Plus, User, Download, Refresh } from '@element-plus/icons-vue'
import request, { exportCsv, uploadImage } from '../../utils/request'

const queryParams = reactive({
  title: '',
  resume: '',
  field: '',
  level: '',
})

const loading = ref(false)
const tableData = ref<any[]>([])
const allData = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const statusFilter = ref('all')

const dialogForm = reactive({
  id: undefined,
  name: '',
  avatar: '',
  introduction: '',
  title: '',
  organization: '',
  specialty: '',
  status: 1,
})

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request.get('/dev-api/yjnb/expert/list')
    if (res.code === 200) {
      console.log('专家列表原始数据:', res.rows)
      allData.value = (res.rows || []).map((item: any) => {
        console.log('专家数据:', item.name, 'avatar长度:', item.avatar?.length)
        return {
          ...item,
          // 兼容旧字段名用于显示
          image: item.avatar || '',
          field: item.specialty || '农业技术',
          catgory: item.title || '教授',
          resume: item.introduction || '',
          author: item.organization || '',
          publishTime: item.publishTime || item.createTime || item.updateTime || '',
          publishStatus: item.status ?? 0,
          browseNum: item.browseNum ?? item.serviceCount ?? 0,
          accountId: item.updateTime ? formatDate(new Date(new Date(item.updateTime).getTime() + 365 * 24 * 60 * 60 * 1000)) : 'N/A',
        }
      })
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
  }
  
  // 搜索筛选
  if (queryParams.title.trim()) {
    const keyword = queryParams.title.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.name && item.name.toLowerCase().includes(keyword)) ||
      (item.introduction && item.introduction.toLowerCase().includes(keyword))
    )
  }
  
  if (queryParams.resume.trim()) {
    const resume = queryParams.resume.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.introduction && item.introduction.toLowerCase().includes(resume))
    )
  }
  
  if (queryParams.field) {
    filteredData = filteredData.filter(item => {
      const field = String(item.specialty || item.field || '')
      return field.includes(queryParams.field)
    })
  }
  
  if (queryParams.level) {
    filteredData = filteredData.filter(item => {
      const title = String(item.title || item.catgory || '')
      return title.includes(queryParams.level)
    })
  }
  
  total.value = filteredData.length
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  tableData.value = filteredData.slice(start, end)
}

const handleQuery = () => {
  currentPage.value = 1
  applyFilters()
}

const handleReset = () => {
  queryParams.title = ''
  queryParams.resume = ''
  queryParams.field = ''
  queryParams.level = ''
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
    name: '',
    avatar: '',
    introduction: '',
    title: '',
    organization: '',
    specialty: '',
    status: 1,
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(dialogForm, {
    ...row,
    status: row.status ?? row.publishStatus ?? 0,
  })
  dialogVisible.value = true
}

const handleStatusChange = async (row: any) => {
  const nextStatus = row.publishStatus
  const oldStatus = nextStatus === 1 ? 0 : 1

  try {
    const res = await request.put('/dev-api/yjnb/expert', {
      id: row.id,
      status: nextStatus,
    })

    if (res.code === 200) {
      row.status = nextStatus
      const sourceRow = allData.value.find(item => item.id === row.id)
      if (sourceRow) {
        sourceRow.status = nextStatus
        sourceRow.publishStatus = nextStatus
      }
      ElMessage.success(nextStatus === 1 ? '发布成功' : '取消发布成功')
    } else {
      row.publishStatus = oldStatus
      ElMessage.error(res.msg || '状态更新失败')
    }
  } catch (error) {
    row.publishStatus = oldStatus
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  }
}

const submitForm = async () => {
  if (!dialogForm.name) {
    ElMessage.warning('请输入专家姓名')
    return
  }

  try {
    const submitData = { ...dialogForm }
    
    // 如果是新增，删除id字段，让后端自动生成
    if (!isEdit.value) {
      delete submitData.id
    }
    
    let res
    if (isEdit.value) {
      res = await request.put('/dev-api/yjnb/expert', submitData)
    } else {
      res = await request.post('/dev-api/yjnb/expert', submitData)
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
  ElMessageBox.confirm('确定要删除该专家信息吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await request.delete(`/dev-api/yjnb/expert/${row.id}`)
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

const handleExport = () => {
  exportCsv('专家列表', [
    { title: '专家姓名', key: 'name' },
    { title: '头衔', key: 'catgory' },
    { title: '专家简介', key: 'resume' },
    { title: '所属院题', key: 'author' },
    { title: '专家领域', key: 'field' },
    { title: '发布时间', key: 'publishTime' },
    { title: '发布状态', key: 'publishStatus' },
    { title: '浏览数', key: 'browseNum' },
  ], tableData.value)
  ElMessage.success('导出成功')
}

const handleImageChange = async (file: any) => {
  if (!file.raw) return

  try {
    const result = await uploadImage(file.raw)
    dialogForm.avatar = result.url
    ElMessage.success('图片上传成功')
  } catch (error: any) {
    console.error('专家照片上传失败:', error)
    ElMessage.error(error?.message || '图片上传失败')
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  applyFilters()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  applyFilters()
}

const formatDate = (dateStr: string | Date) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.expert-management {
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

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 14px;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  margin: 0 40px 20px 40px !important;
  border: 1px solid #e8e8e8;
  width: calc(100% - 80px) !important;
}

:deep(.el-table th) {
  background: #1890ff !important;
  color: #fff;
  font-weight: 500;
  font-size: 14px;
  padding: 12px 0;
}

:deep(.el-table th .cell) {
  color: #fff;
}

:deep(.el-table td) {
  padding: 10px 0;
  border-color: #e8dcc8;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f5f5 !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped) {
  background-color: #fafaf8;
}

:deep(.el-table td), :deep(.el-table th) {
  border-color: #e8dcc8;
}

:deep(.el-table::before) {
  background-color: #e8dcc8;
}

:deep(.el-table--border .el-table__inner-wrapper::after) {
  background-color: #e8dcc8;
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
  width: 148px;
  height: 148px;
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
  width: 148px;
  height: 148px;
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
</style>
