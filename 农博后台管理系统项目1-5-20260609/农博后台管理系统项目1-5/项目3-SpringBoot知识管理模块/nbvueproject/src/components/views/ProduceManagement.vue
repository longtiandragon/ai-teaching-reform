<template>
  <div class="produce-management">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><ShoppingBag /></el-icon>
        <span class="header-title">农产品管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增农产品</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="queryParams.title"
          placeholder="搜索农产品名称或卖点摘要"
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
          placeholder="请输入产品摘要"
          clearable
          class="filter-input"
          @keyup.enter="handleQuery"
        />
        <el-select v-model="queryParams.pushStatus" placeholder="上架状态" clearable class="filter-select" @change="handleQuery">
          <el-option label="已上架" :value="1" />
          <el-option label="未上架" :value="0" />
        </el-select>
        <el-select v-model="queryParams.recommend" placeholder="推荐状态" clearable class="filter-select" @change="handleQuery">
          <el-option label="已推荐" :value="1" />
          <el-option label="未推荐" :value="0" />
        </el-select>
        <el-input-number
          v-model="queryParams.salesMin"
          placeholder="最小销量"
          :min="0"
          controls-position="right"
          class="filter-number"
          @change="handleQuery"
        />
        <el-input-number
          v-model="queryParams.browseMin"
          placeholder="最小浏览量"
          :min="0"
          controls-position="right"
          class="filter-number"
          @change="handleQuery"
        />
        <el-button type="primary" :icon="Search" @click="handleQuery">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>

      <div class="filter-buttons">
        <span class="filter-label">快捷筛选：</span>
        <el-button :type="statusFilter === 'all' ? 'primary' : 'default'" size="small" @click="filterByStatus('all')">
          全部
        </el-button>
        <el-button :type="statusFilter === 'unpushed' ? 'primary' : 'default'" size="small" @click="filterByStatus('unpushed')">
          未上架
        </el-button>
        <el-button :type="statusFilter === 'recommend' ? 'primary' : 'default'" size="small" @click="filterByStatus('recommend')">
          推荐商品
        </el-button>
      </div>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="序号" width="70" align="center" />
      <el-table-column prop="title" label="农产品名称" width="160" show-overflow-tooltip />
      <el-table-column label="图片" width="90" align="center">
        <template #default="scope">
          <el-image
            v-if="scope.row.image"
            :src="scope.row.image"
            fit="cover"
            class="table-image"
            :preview-src-list="[scope.row.image]"
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <span v-else class="empty-text">暂无</span>
        </template>
      </el-table-column>
      <el-table-column prop="providerName" label="商户名称" width="140" align="center" />
      <el-table-column prop="resume" label="产品摘要" min-width="180" show-overflow-tooltip />
      <el-table-column label="上架状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.pushStatus === 1 ? 'success' : 'info'" size="small">
            {{ scope.row.pushStatus === 1 ? '已上架' : '未上架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="pushTime" label="上架时间" width="120" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.pushTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="browseNum" label="浏览数" width="90" align="center" />
      <el-table-column label="操作" width="240" align="center">
        <template #default="scope">
          <div class="action-btns">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)" plain>编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)" plain>删除</el-button>
            <el-button
              :type="scope.row.recommend === 1 ? 'warning' : 'success'"
              size="small"
              @click="toggleRecommend(scope.row)"
              plain
            >
              {{ scope.row.recommend === 1 ? '取消推荐' : '推荐' }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100, 160]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      class="pagination"
    />

    <el-dialog v-model="dialogVisible" :title="isEdit ? '修改农产品' : '新增农产品'" width="600px">
      <el-form :model="dialogForm" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="产品名称" prop="title">
          <el-input v-model="dialogForm.title" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品图片">
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
              <p>点击上传图片或输入图片URL</p>
              <el-input v-model="dialogForm.image" placeholder="或直接输入图片URL" clearable size="small" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="产品摘要" prop="resume">
          <el-input v-model="dialogForm.resume" type="textarea" :rows="2" placeholder="请输入产品摘要" />
        </el-form-item>
        <el-form-item label="产品详情">
          <el-input v-model="dialogForm.description" type="textarea" :rows="3" placeholder="请输入产品详情" />
        </el-form-item>
        <el-form-item label="产品品类">
          <el-select v-model="dialogForm.catgory" placeholder="请选择产品品类" style="width: 100%;">
            <el-option label="粮食" value="粮食" />
            <el-option label="蔬菜" value="蔬菜" />
            <el-option label="水果" value="水果" />
            <el-option label="禽蛋" value="禽蛋" />
            <el-option label="茶叶" value="茶叶" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="商户名称">
          <el-input v-model="dialogForm.providerName" placeholder="请输入商户名称" />
        </el-form-item>
        <el-form-item label="产品价格" prop="price">
          <el-input-number v-model="dialogForm.price" :min="0" :precision="2" :step="0.1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="上架状态">
          <el-radio-group v-model="dialogForm.pushStatus">
            <el-radio :label="1">已上架</el-radio>
            <el-radio :label="0">未上架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="推荐状态">
          <el-radio-group v-model="dialogForm.recommend">
            <el-radio :label="1">已推荐</el-radio>
            <el-radio :label="0">未推荐</el-radio>
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
import { Search, Picture, Plus, Download, Refresh, ShoppingBag } from '@element-plus/icons-vue'
import request, { exportCsv, uploadImage } from '../../utils/request'

const queryParams = reactive<{
  title: string
  resume: string
  pushStatus?: number
  recommend?: number
  salesMin?: number
  browseMin?: number
}>({
  title: '',
  resume: '',
  pushStatus: undefined,
  recommend: undefined,
  salesMin: undefined,
  browseMin: undefined,
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
const formRef = ref<any>()
let fetchingData = false

const dialogForm = reactive<any>({
  id: undefined,
  title: '',
  image: '',
  resume: '',
  description: '',
  catgory: '',
  providerName: '',
  price: 0,
  pushStatus: 0,
  recommend: 0,
})

const rules = {
  title: [{ required: true, message: '产品名称不能为空', trigger: 'blur' }],
  resume: [{ required: true, message: '产品摘要不能为空', trigger: 'blur' }],
  price: [{ required: true, message: '产品价格不能为空', trigger: 'blur' }],
}

const fetchList = async () => {
  if (fetchingData) return
  fetchingData = true
  loading.value = true
  try {
    const res: any = await request.get('/dev-api/yjnb/produce/list')
    if (res.code === 200) {
      allData.value = res.rows || []
      applyFilters()
    }
  } catch (error) {
    console.error('获取农产品列表失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
    fetchingData = false
  }
}

const applyFilters = () => {
  let filteredData = [...allData.value]

  if (statusFilter.value === 'unpushed') {
    filteredData = filteredData.filter(item => item.pushStatus === 0)
  } else if (statusFilter.value === 'recommend') {
    filteredData = filteredData.filter(item => item.recommend === 1)
  }

  if (queryParams.title.trim()) {
    const keyword = queryParams.title.trim().toLowerCase()
    filteredData = filteredData.filter(item =>
      (item.title && item.title.toLowerCase().includes(keyword)) ||
      (item.resume && item.resume.toLowerCase().includes(keyword))
    )
  }

  if (queryParams.resume.trim()) {
    const resume = queryParams.resume.trim().toLowerCase()
    filteredData = filteredData.filter(item => item.resume && item.resume.toLowerCase().includes(resume))
  }

  if (queryParams.pushStatus !== undefined) {
    filteredData = filteredData.filter(item => item.pushStatus === queryParams.pushStatus)
  }

  if (queryParams.recommend !== undefined) {
    filteredData = filteredData.filter(item => item.recommend === queryParams.recommend)
  }

  if (queryParams.salesMin !== undefined && queryParams.salesMin !== null) {
    filteredData = filteredData.filter(item => (item.salesNum || 0) >= (queryParams.salesMin || 0))
  }

  if (queryParams.browseMin !== undefined && queryParams.browseMin !== null) {
    filteredData = filteredData.filter(item => (item.browseNum || 0) >= (queryParams.browseMin || 0))
  }

  total.value = filteredData.length
  const start = (currentPage.value - 1) * pageSize.value
  tableData.value = filteredData.slice(start, start + pageSize.value)
}

const handleQuery = () => {
  currentPage.value = 1
  applyFilters()
}

const handleReset = () => {
  queryParams.title = ''
  queryParams.resume = ''
  queryParams.pushStatus = undefined
  queryParams.recommend = undefined
  queryParams.salesMin = undefined
  queryParams.browseMin = undefined
  statusFilter.value = 'all'
  currentPage.value = 1
  applyFilters()
}

const filterByStatus = (status: string) => {
  statusFilter.value = status
  currentPage.value = 1
  applyFilters()
}

const resetDialogForm = () => {
  Object.assign(dialogForm, {
    id: undefined,
    title: '',
    image: '',
    resume: '',
    description: '',
    catgory: '',
    providerName: '',
    price: 0,
    pushStatus: 0,
    recommend: 0,
  })
}

const handleAdd = () => {
  isEdit.value = false
  resetDialogForm()
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
      const submitData: any = { ...dialogForm }
      if (!isEdit.value) delete submitData.id
      const res: any = isEdit.value
        ? await request.put('/dev-api/yjnb/produce', submitData)
        : await request.post('/dev-api/yjnb/produce', submitData)

      if (res.code === 200) {
        ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
        dialogVisible.value = false
        fetchList()
      } else {
        ElMessage.error(res.msg || '操作失败')
      }
    } catch (error: any) {
      console.error('提交农产品失败:', error)
      ElMessage.error(error?.message || '操作失败')
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该农产品吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.delete(`/dev-api/yjnb/produce/${row.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchList()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除农产品失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const toggleRecommend = (row: any) => {
  const action = row.recommend === 1 ? '取消推荐' : '推荐'
  ElMessageBox.confirm(`是否${action}所选商品？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info',
  }).then(async () => {
    try {
      const res: any = row.recommend === 1
        ? await request.post('/dev-api/yjnb/produce/unrecommendFarmProduce', [row.id])
        : await request.post('/dev-api/yjnb/produce/recommendFarmProduce', [row.id])

      if (res.code === 200) {
        ElMessage.success(`${action}成功`)
        row.recommend = row.recommend === 1 ? 0 : 1
        applyFilters()
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
  exportCsv('农产品列表', [
    { title: '农产品名称', key: 'title' },
    { title: '图片', key: 'image' },
    { title: '商户名称', key: 'providerName' },
    { title: '产品摘要', key: 'resume' },
    { title: '产品品类', key: 'catgory' },
    { title: '价格', key: 'price' },
    { title: '上架状态', key: 'pushStatus' },
    { title: '推荐状态', key: 'recommend' },
    { title: '浏览数', key: 'browseNum' },
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
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '-'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.produce-management {
  width: 100%;
  padding: 0;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
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

.header-right,
.search-row,
.filter-buttons,
.action-btns {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-section {
  background: #fff;
  padding: 20px;
  margin: 20px 40px;
  border: 1px solid #e8e8e8;
}

.search-input {
  width: 300px;
}

.filter-input,
.filter-select {
  width: 180px;
}

.filter-number {
  width: 150px;
}

.filter-buttons {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

.filter-label {
  font-size: 14px;
  color: #606266;
}

:deep(.el-table) {
  margin: 0 40px 20px 40px;
  width: calc(100% - 80px) !important;
  border: 1px solid #e8e8e8;
}

:deep(.el-table th) {
  background: #1890ff !important;
  color: #fff;
  font-weight: 600;
}

.table-image,
.image-slot {
  width: 60px;
  height: 60px;
  border-radius: 4px;
}

.image-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.empty-text {
  color: #c0c4cc;
  font-size: 12px;
}

.pagination {
  margin: 20px 40px;
  justify-content: flex-end;
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
  overflow: hidden;
  cursor: pointer;
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
  color: #8c939d;
  font-size: 28px;
}

.upload-tips {
  flex: 1;
  color: #606266;
}

.upload-tips p {
  margin: 0 0 8px;
}
</style>
