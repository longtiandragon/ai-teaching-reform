<template>
  <div class="service-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Tools /></el-icon>
        <span class="header-title">农事服务管理</span>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增服务</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域-->
    <div class="search-section">
      <div class="search-row">
        <el-input
          v-model="searchKeyword"
          placeholder="输入标题/摘要搜索"
          clearable
          @keyup.enter="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select 
          v-model="searchCategory" 
          placeholder="服务类别" 
          clearable
          style="width: 150px; margin-left: 10px;"
          @change="handleSearch"
        >
          <el-option label="农技指导" value="guidance" />
          <el-option label="农机服务" value="machinery" />
          <el-option label="植保服务" value="protection" />
          <el-option label="农资供应" value="supply" />
          <el-option label="信息咨询" value="consultation" />
        </el-select>

        <el-select 
          v-model="searchStatus" 
          placeholder="服务状态" 
          clearable
          style="width: 120px; margin-left: 10px;"
          @change="handleSearch"
        >
          <el-option label="服务中" :value="1" />
          <el-option label="已结束" :value="0" />
        </el-select>

        <el-button type="primary" @click="handleSearch" style="margin-left: 10px;">
          <el-icon><Search /></el-icon> 搜索
        </el-button>
      </div>

      <!-- 操作按钮组-->
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增服务
        </el-button>
        <el-button 
          :type="statusFilter === 'all' ? 'primary' : ''"
          @click="filterByStatus('all')"
        >全部</el-button>
        <el-button 
          :type="statusFilter === 'active' ? 'success' : ''"
          @click="filterByStatus('active')"
        >服务中</el-button>
        <el-button 
          :type="statusFilter === 'hot' ? 'warning' : ''"
          @click="filterByStatus('hot')"
        >热门服务</el-button>
        <el-button @click="handleExport">批量导出</el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      border
      stripe
      v-loading="loading"
      class="modern-table"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="title" label="服务标题" width="180" show-overflow-tooltip />
      
      <el-table-column label="图片" width="100" align="center">
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

      <el-table-column prop="provider" label="服务中" width="140" align="center" />
      <el-table-column prop="resume" label="服务摘要" min-width="200" show-overflow-tooltip />
      
      <el-table-column prop="category" label="服务类别" width="120" align="center">
        <template #default="scope">
          <el-tag :type="getCategoryType(scope.row.category)" size="small">
            {{ getCategoryText(scope.row.category) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="price" label="服务价格" width="120" align="center">
        <template #default="scope">
          <span style="color: #f56c6c; font-weight: 600;">
            {{ scope.row.price === 0 ? '免费' : '¥' + scope.row.price }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column label="服务状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 1 ? 'success' : 'info'" size="small">
            {{ scope.row.status === 1 ? '服务中' : '已结束' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="orderCount" label="预约量" width="100" align="center">
        <template #default="scope">
          <span style="color: #409eff; font-weight: 600;">{{ scope.row.orderCount }}</span>
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
              @click="toggleStatus(scope.row)"
              plain>
              {{ scope.row.status === 1 ? '下线' : '上线' }}
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
      :title="isEdit ? '修改农事服务' : '新增农事服务'" 
      width="750px"
      class="modern-dialog"
    >
      <el-form :model="dialogForm" label-width="100px" :rules="rules" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务标题" prop="title">
              <el-input v-model="dialogForm.title" placeholder="请输入服务标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务类别" prop="category">
              <el-select v-model="dialogForm.category" placeholder="请选择" style="width: 100%;">
                <el-option label="农技指导" value="guidance" />
                <el-option label="农机服务" value="machinery" />
                <el-option label="植保服务" value="protection" />
                <el-option label="农资供应" value="supply" />
                <el-option label="信息咨询" value="consultation" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="服务图片">
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
              <p>点击上传服务图片（推荐尺寸：400x240）</p>
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

        <el-form-item label="服务摘要" prop="resume">
          <el-input v-model="dialogForm.resume" type="textarea" :rows="2" placeholder="请输入服务摘要" />
        </el-form-item>

        <el-form-item label="服务详情">
          <el-input v-model="dialogForm.content" type="textarea" :rows="4" placeholder="请输入服务详细内容" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务中" prop="provider">
              <el-input v-model="dialogForm.provider" placeholder="请输入服务商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="dialogForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务价格" prop="price">
              <el-input-number v-model="dialogForm.price" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务状态">
              <el-radio-group v-model="dialogForm.status">
                <el-radio :label="1">服务中</el-radio>
                <el-radio :label="0">已结束</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="服务地址">
          <el-input v-model="dialogForm.address" placeholder="请输入服务地址" />
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
import { Search, Plus, Picture, Tools, Download, Refresh } from '@element-plus/icons-vue'
import request, { exportCsv, uploadImage } from '../../utils/request'

const searchKeyword = ref('')
const searchCategory = ref('')
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
  resume: '',
  content: '',
  category: '',
  provider: '',
  phone: '',
  price: 0,
  status: 1,
  address: '',
  orderCount: 0,
  rating: 5
})

const rules = {
  title: [{ required: true, message: '服务标题不能为空', trigger: 'blur' }],
  category: [{ required: true, message: '请选择服务类别', trigger: 'change' }],
  resume: [{ required: true, message: '服务摘要不能为空', trigger: 'blur' }],
  provider: [{ required: true, message: '服务商名称不能为题', trigger: 'blur' }],
  price: [{ required: true, message: '请输入服务价题', trigger: 'blur' }],
}

// 模拟数据
const mockData = [
  {
    id: 1,
    title: '有机肥料配送服务',
    image: 'https://via.placeholder.com/400x240/67c23a/fff?text=有机肥料',
    resume: '提供优质有机肥料，全程冷链配送，确保肥料新鲜',
    content: '我们提供最优质的有机肥料，来源可追溯，质量有保障。专业团队提供施肥指导，确保农作物健康成长',
    category: 'supply',
    provider: '绿色农资公司',
    phone: '400-888-8888',
    price: 120,
    status: 1,
    address: '浙江省杭州市余杭区',
    orderCount: 358,
    rating: 4.8
  },
  {
    id: 2,
    title: '农机租赁与维修服务',
    image: 'https://via.placeholder.com/400x240/409eff/fff?text=农机服务',
    resume: '提供各类农机租赁服务，包括拖拉机、收割机、播种机等',
    content: '专业农机租赁服务，设备齐全，价格优惠。提供上门维修保养服务，确保农机正常运转',
    category: 'machinery',
    provider: '农机服务中心',
    phone: '400-777-7777',
    price: 200,
    status: 1,
    address: '山东省济南市历城区',
    orderCount: 245,
    rating: 4.5
  },
  {
    id: 3,
    title: '病虫害防治指导',
    image: 'https://via.placeholder.com/400x240/e6a23c/fff?text=植保服务',
    resume: '专业农技专家提供病虫害识别与防治方案',
    content: '拥有多年经验的农技专家团队，为您提供精准的病虫害诊断和科学的防治方案，保障作物健康生长',
    category: 'protection',
    provider: '农技推广站',
    phone: '400-666-6666',
    price: 0,
    status: 1,
    address: '江苏省南京市江宁区',
    orderCount: 489,
    rating: 4.9
  },
  {
    id: 4,
    title: '种植技术培训课程',
    image: 'https://via.placeholder.com/400x240/f56c6c/fff?text=技术培训',
    resume: '系统化的种植技术培训，从基础到进阶全方位覆盖',
    content: '提供线上线下相结合的培训课程，包括土壤管理、施肥技巧、病虫害防治等多个专题，助您成为种植达人',
    category: 'guidance',
    provider: '农业培训学院',
    phone: '400-555-5555',
    price: 299,
    status: 1,
    address: '广东省广州市天河区',
    orderCount: 567,
    rating: 5.0
  },
]

const getCategoryType = (category: string) => {
  const types: any = {
    'guidance': 'success',
    'machinery': 'warning',
    'protection': 'danger',
    'supply': 'primary',
    'consultation': 'info'
  }
  return types[category] || 'info'
}

const getCategoryText = (category: string) => {
  const texts: any = {
    'guidance': '农技指导',
    'machinery': '农机服务',
    'protection': '植保服务',
    'supply': '农资供应',
    'consultation': '信息咨询'
  }
  return texts[category] || category
}

// 从数据库加载数据
const fetchList = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/dev-api/yjnb/service/list')
    if (res.code === 200) {
      allData.value = res.rows || []
      console.log('从数据库加载了', allData.value.length, '条服务数据')
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
  if (statusFilter.value === 'active') {
    filteredData = filteredData.filter(item => item.status === 1)
  } else if (statusFilter.value === 'hot') {
    filteredData = filteredData.filter(item => item.orderCount > 300)
  }
  
  // 搜索筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filteredData = filteredData.filter(item => 
      (item.title && item.title.toLowerCase().includes(keyword)) ||
      (item.resume && item.resume.toLowerCase().includes(keyword))
    )
  }
  
  if (searchCategory.value) {
    filteredData = filteredData.filter(item => item.category === searchCategory.value)
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
    resume: '',
    content: '',
    category: '',
    provider: '',
    phone: '',
    price: 0,
    status: 1,
    address: '',
    orderCount: 0,
    rating: 5
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
        res = await request.put('/dev-api/yjnb/service', submitData)
      } else {
        res = await request.post('/dev-api/yjnb/service', submitData)
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
  ElMessageBox.confirm('确定要删除该农事服务吗？', '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res: any = await request.delete(`/dev-api/yjnb/service/${row.id}`)
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

const toggleStatus = (row: any) => {
  const action = row.status === 1 ? '下线' : '上线'
  ElMessageBox.confirm(`确定要${action}该服务吗？`, '系统提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    const index = allData.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      allData.value[index].status = row.status === 1 ? 0 : 1
      ElMessage.success(`${action}成功`)
      applyFilters()
    }
  }).catch(() => {})
}

const handleExport = () => {
  exportCsv('农事服务列表', [
    { title: '服务标题', key: 'title' },
    { title: '图片', key: 'image' },
    { title: '服务摘要', key: 'resume' },
    { title: '服务类别', key: 'category' },
    { title: '服务商', key: 'provider' },
    { title: '电话', key: 'phone' },
    { title: '价格', key: 'price' },
    { title: '状态', key: 'status' },
    { title: '预约量', key: 'orderCount' },
    { title: '评分', key: 'rating' },
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

onMounted(() => {
  initData()
})
</script>

<style scoped>
.service-management {
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

.search-section {
  background: white;
  padding: 20px;
  margin: 20px 40px;
  border: 1px solid #e8e8e8;
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
.modern-table {
  margin: 0 40px 20px 40px;
  border: 1px solid #e8e8e8;
  width: calc(100% - 80px) !important;
}

:deep(.modern-table th) {
  background: #1890ff !important;
  color: white !important;
  font-weight: 500;
  font-size: 14px;
}

:deep(.modern-table th .cell) {
  color: white;
}

:deep(.modern-table td) {
  border-color: #e8dcc8;
}

:deep(.modern-table td), :deep(.modern-table th) {
  border-color: #e8dcc8;
}

:deep(.modern-table .el-table__row:hover > td) {
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

/* 对话框样式*/
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

/* 按钮样式覆盖 */
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
  height: 140px;
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
  height: 140px;
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
</style>
