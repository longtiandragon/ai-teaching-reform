<template>
  <div class="market-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Shop /></el-icon>
        <span class="header-title">农贸市场管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增市场</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域-->
    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="searchKeyword"
          placeholder="输入农贸市场名称搜索"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-input
          v-model="searchRegion"
          placeholder="请输入所在地区"
          clearable
          class="filter-input"
          @keyup.enter="handleSearch"
        />

        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>

      <!-- 快捷筛选标题-->
      <div class="filter-tags">
        <span class="filter-label">快捷筛选：</span>
        <el-tag
          :type="regionFilter === 'all' ? 'primary' : 'info'"
          :effect="regionFilter === 'all' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByRegion('all')"
        >
          全部地区
        </el-tag>
        <el-tag
          :type="regionFilter === '城市' ? 'success' : 'info'"
          :effect="regionFilter === '城市' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByRegion('城市')"
        >
          城市市场
        </el-tag>
        <el-tag
          :type="regionFilter === '郊区' ? 'warning' : 'info'"
          :effect="regionFilter === '郊区' ? 'dark' : 'plain'"
          class="filter-tag"
          @click="filterByRegion('郊区')"
        >
          郊区市场
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
      <el-table-column prop="name" label="市场名称" width="200" show-overflow-tooltip />
      <el-table-column label="市场图片" width="100" align="center">
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
      <el-table-column prop="regionId" label="所在地区" width="150" align="center" />
      <el-table-column prop="remark" label="市场简介" min-width="300" show-overflow-tooltip />
      <el-table-column prop="createTime" label="创建时间" width="180" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.createTime) }}
        </template>
      </el-table-column>
      
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
      :title="isEdit ? '修改农贸市场' : '新增农贸市场'" 
      width="500px"
    >
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="市场名称" required>
          <el-input v-model="dialogForm.name" placeholder="请输入市场名称" />
        </el-form-item>
        <el-form-item label="所在地区">
          <el-input v-model="dialogForm.regionId" placeholder="请输入所在地区" />
        </el-form-item>
        <el-form-item label="市场图片">
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
              <p>点击上传市场图片</p>
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
        <el-form-item label="备注">
          <el-input v-model="dialogForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { Search, Shop, Plus, Download, Refresh, Picture } from '@element-plus/icons-vue'
import request, { exportCsv, uploadImage } from '../../utils/request'

const searchKeyword = ref('')
const searchRegion = ref('')
const loading = ref(false)
const tableData = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const allData = ref<any[]>([])
const statusFilter = ref('all')
const regionFilter = ref('all')

const dialogForm = reactive({
  id: null,
  name: '',
  regionId: '',
  image: '',
  remark: ''
})

const fetchList = async () => {
  loading.value = true
  try {
    console.log('🔄 开始获取市场列表...')
    const res = await request.get('/dev-api/yjnb/market/list')
    console.log('📦 后端原始响应:', res)
    
    if (res && res.code === 200) {
      allData.value = (res.rows || []).map((item: any) => ({
        ...item,
        createTime: item.createTime || item.createdTime || '-',
        image: item.image || '',
        remark: item.remark || '暂无简介'
      }))
    } else {
      allData.value = []
      ElMessage.error(res?.msg || '获取市场列表失败')
    }
    applyFilters()
    
  } catch (error) {
    console.error('API请求失败:', error)
    allData.value = []
    applyFilters()
    ElMessage.error('后端服务未启动或接口请求失败')
    
  } finally {
    loading.value = false
    console.log('✅ fetchList完成,当前tableData条数:', tableData.value.length)
  }
}

const applyFilters = () => {
  let filteredData = [...allData.value]
  
  // 地区筛选
  if (regionFilter.value !== 'all') {
    filteredData = filteredData.filter(item => 
      item.regionId && item.regionId.includes(regionFilter.value)
    )
  }
  
  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.name && item.name.toLowerCase().includes(keyword)) ||
      (item.remark && item.remark.toLowerCase().includes(keyword))
    )
  }
  
  if (searchRegion.value.trim()) {
    const region = searchRegion.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.regionId && item.regionId.toLowerCase().includes(region))
    )
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
  searchRegion.value = ''
  regionFilter.value = 'all'
  currentPage.value = 1
  applyFilters()
}

const filterByStatus = (status: string) => {
  statusFilter.value = status
  currentPage.value = 1
  applyFilters()
}

const filterByRegion = (region: string) => {
  regionFilter.value = region
  currentPage.value = 1
  applyFilters()
}

const resetForm = () => {
  dialogForm.id = null
  dialogForm.name = ''
  dialogForm.regionId = ''
  dialogForm.image = ''
  dialogForm.remark = ''
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
  if (!dialogForm.name) {
    ElMessage.warning('请输入市场名称')
    return
  }

  try {
    let res
    if (isEdit.value) {
      res = await request.put('/dev-api/yjnb/market', dialogForm)
    } else {
      res = await request.post('/dev-api/yjnb/market', dialogForm)
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
  ElMessageBox.confirm('确定要删除该农贸市场吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await request.delete(`/dev-api/yjnb/market/${row.id}`)
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
  exportCsv('农贸市场列表', [
    { title: '市场名称', key: 'name' },
    { title: '所在地区', key: 'regionId' },
    { title: '市场图片', key: 'image' },
    { title: '市场简介', key: 'remark' },
    { title: '创建时间', key: 'createTime' },
  ], tableData.value)
  ElMessage.success('导出成功')
}

const handleImageChange = async (file: any) => {
  if (!file.raw) return

  try {
    const result = await uploadImage(file.raw)
    dialogForm.image = result.url
    ElMessage.success('图片上传成功')
  } catch (error: any) {
    console.error('图片上传失败:', error)
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

const formatDate = (dateStr: string) => {
  if (!dateStr || dateStr === 'null' || dateStr === 'undefined') return '-'
  
  // 如果已经是正确的格式,直接返回(YYYY-MM-DD HH:mm:ss)
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(dateStr)) {
    return dateStr.substring(0, 16) // 返回 YYYY-MM-DD HH:mm
  }
  
  // 尝试解析日期
  const date = new Date(dateStr)
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    console.error('❌ 无效的日期格式:', dateStr)
    return '-'
  }
  
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  // ✅ 直接从数据库获取数据
  fetchList()
})
</script>

<style scoped>
.market-management {
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

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 14px;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  margin: 0 40px 20px 40px;
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

.image-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 22px;
}

.image-upload-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.image-uploader {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
}

.image-uploader:hover {
  border-color: #1890ff;
}

.preview-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  display: block;
}

.uploader-icon {
  width: 120px;
  height: 120px;
  font-size: 28px;
  color: #8c939d;
}

.upload-tips {
  flex: 1;
  color: #8b7355;
  font-size: 13px;
}

.upload-tips p {
  margin: 0;
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
