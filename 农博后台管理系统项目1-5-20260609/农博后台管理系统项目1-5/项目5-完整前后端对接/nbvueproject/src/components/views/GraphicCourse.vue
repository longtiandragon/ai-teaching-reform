<template>
  <div class="graphic-course">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><Reading /></el-icon>
        <span class="header-title">图文课程管理</span>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-form :model="queryParams" :inline="true" class="search-form">
        <el-form-item label="课程标题">
          <el-input
            v-model="queryParams.title"
            placeholder="请输入课程标题"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="讲师姓名">
          <el-input
            v-model="queryParams.teacher"
            placeholder="请输入讲师姓名"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="课程分类">
          <el-select v-model="queryParams.category" placeholder="请选择课程分类" clearable>
            <el-option label="种植技术" value="种植技术" />
            <el-option label="果树管理" value="果树管理" />
            <el-option label="病虫害防治" value="病虫害防治" />
            <el-option label="智慧农业" value="智慧农业" />
            <el-option label="经营管理" value="经营管理" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布状态">
          <el-select v-model="queryParams.publishStatus" placeholder="请选择发布状态" clearable>
            <el-option label="未发布" :value="0" />
            <el-option label="已发布" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 快捷筛选标题-->
    <div class="filter-tags">
      <el-tag
        :type="queryParams.category === null ? 'success' : ''"
        @click="filterByCategory(null)"
        class="filter-tag"
      >
        全部分类
      </el-tag>
      <el-tag
        v-for="cat in categories"
        :key="cat"
        :type="queryParams.category === cat ? 'success' : ''"
        @click="filterByCategory(cat)"
        class="filter-tag"
      >
        {{ cat }}
      </el-tag>
    </div>

    <!-- 工具题-->
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增课程</el-button>
      <el-button :icon="Download" @click="handleExport">批量导出</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table :data="courseList" v-loading="loading" border>
      <el-table-column label="序号" type="index" width="60" align="center" />
      <el-table-column label="课程标题" prop="title" min-width="200" show-overflow-tooltip />
      <el-table-column label="讲师" prop="teacher" width="100" align="center" />
      <el-table-column label="分类" prop="category" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="getCategoryType(row.category)" size="small">
            {{ row.category }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="封面" width="90" align="center">
        <template #default="{ row }">
          <el-image
            v-if="row.image"
            :src="row.image"
            :preview-src-list="[row.image]"
            fit="cover"
            class="table-image"
          />
        </template>
      </el-table-column>
      <el-table-column label="浏览" prop="browseNum" width="80" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.publishStatus === 1 ? 'success' : 'info'" size="small">
            {{ row.publishStatus === 1 ? '已发布' : '未发布' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="推荐" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.recommend"
            :active-value="1"
            :inactive-value="0"
            @change="toggleRecommend(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createTime" width="160" align="center" />
      <el-table-column label="操作" width="300" align="center">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button plain size="small" :icon="View" @click="handleView(row)">查看</el-button>
            <el-button plain size="small" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button
              plain
              size="small"
              :type="row.publishStatus === 1 ? 'warning' : 'success'"
              @click="handlePublish(row)"
            >
              {{ row.publishStatus === 1 ? '取消发布' : '发布' }}
            </el-button>
            <el-button plain size="small" type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="queryParams.pageNum"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="getList"
        @current-change="getList"
      />
    </div>

    <!-- 新增/编辑对话框-->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="dialogForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="课程标题" prop="title">
          <el-input v-model="dialogForm.title" placeholder="请输入课程标题" />
        </el-form-item>
        <el-form-item label="讲师姓名" prop="teacher">
          <el-input v-model="dialogForm.teacher" placeholder="请输入讲师姓名" />
        </el-form-item>
        <el-form-item label="课程分类" prop="category">
          <el-select v-model="dialogForm.category" placeholder="请选择课程分类">
            <el-option label="种植技术" value="种植技术" />
            <el-option label="果树管理" value="果树管理" />
            <el-option label="病虫害防治" value="病虫害防治" />
            <el-option label="智慧农业" value="智慧农业" />
            <el-option label="经营管理" value="经营管理" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图片" prop="image">
          <div class="upload-row">
            <el-upload
              class="cover-uploader"
              :show-file-list="false"
              :auto-upload="false"
              accept="image/*"
              @change="handleImageUpload"
            >
              <img v-if="dialogForm.image" :src="dialogForm.image" class="cover-preview" />
              <el-icon v-else class="upload-icon"><Picture /></el-icon>
            </el-upload>
            <div class="upload-inputs">
              <el-input v-model="dialogForm.image" placeholder="或直接输入图片URL" clearable />
              <el-image
                v-if="dialogForm.image"
                :src="dialogForm.image"
                fit="cover"
                class="preview-image"
              />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="课程简介" prop="resume">
          <el-input
            v-model="dialogForm.resume"
            type="textarea"
            :rows="3"
            placeholder="请输入课程简介"
          />
        </el-form-item>
        <el-form-item label="课程内容" prop="content">
          <el-input
            v-model="dialogForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入课程内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框-->
    <el-dialog
      v-model="viewDialogVisible"
      title="课程详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="课程标题" :span="2">
          {{ viewData.title }}
        </el-descriptions-item>
        <el-descriptions-item label="讲师姓名">
          {{ viewData.teacher }}
        </el-descriptions-item>
        <el-descriptions-item label="课程分类">
          {{ viewData.category }}
        </el-descriptions-item>
        <el-descriptions-item label="浏览数">
          {{ viewData.browseNum }}
        </el-descriptions-item>
        <el-descriptions-item label="发布状态">
          <el-tag :type="viewData.publishStatus === 1 ? 'success' : 'info'">
            {{ viewData.publishStatus === 1 ? '已发布' : '未发布' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="推荐状态">
          <el-tag :type="viewData.recommend === 1 ? 'success' : 'info'">
            {{ viewData.recommend === 1 ? '已推荐' : '未推荐' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ viewData.createTime }}
        </el-descriptions-item>
        <el-descriptions-item label="封面图片" :span="2">
          <el-image v-if="viewData.image" :src="viewData.image" fit="cover" style="width: 200px;" />
        </el-descriptions-item>
        <el-descriptions-item label="课程简介" :span="2">
          {{ viewData.resume }}
        </el-descriptions-item>
        <el-descriptions-item label="课程内容" :span="2">
          <div style="max-height: 300px; overflow-y: auto; white-space: pre-wrap;">
            {{ viewData.content }}
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    </div>
  </template>
  
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Reading,
  Search,
  Refresh,
  Plus,
  Download,
  View,
  Edit,
  Delete,
  Picture
} from '@element-plus/icons-vue'
import request, { exportCsv, uploadImage } from '../../utils/request'

// 数据列表
const courseList = ref([])
const loading = ref(false)
const total = ref(0)

// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  title: null,
  teacher: null,
  category: null,
  publishStatus: null
})

// 分类列表
const categories = ['种植技术', '果树管理', '病虫害防治', '智慧农业', '经营管理']

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogForm = reactive({
  id: null,
  title: '',
  teacher: '',
  category: '',
  image: '',
  resume: '',
  content: ''
})

// 查看详情
const viewDialogVisible = ref(false)
const viewData = ref({})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入课程标题', trigger: 'blur' }],
  teacher: [{ required: true, message: '请输入讲师姓名', trigger: 'blur' }],
  category: [{ required: true, message: '请选择课程分类', trigger: 'change' }]
}

const formRef = ref(null)

// 获取课程列表
const getList = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/dev-api/yjnb/graphicCourse/list', {
      params: queryParams
    })
    if (res.code === 200) {
      courseList.value = res.rows || []
      total.value = res.total || 0
    }
  } catch (error) {
    console.error('获取图文课程列表失败:', error)
    ElMessage.error('获取图文课程列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

// 重置
const handleReset = () => {
  queryParams.pageNum = 1
  queryParams.pageSize = 10
  queryParams.title = null
  queryParams.teacher = null
  queryParams.category = null
  queryParams.publishStatus = null
  getList()
}

// 按分类筛选
const filterByCategory = (category: string | null) => {
  queryParams.category = category
  handleQuery()
}

// 获取分类标签类型
const getCategoryType = (category: string) => {
  const types: any = {
    '种植技术': 'success',
    '果树管理': 'warning',
    '病虫害防治': 'danger',
    '智慧农业': 'primary',
    '经营管理': 'info'
  }
  return types[category] || ''
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增图文课程'
  Object.assign(dialogForm, {
    id: null,
    title: '',
    teacher: '',
    category: '',
    image: '',
    resume: '',
    content: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑图文课程'
  Object.assign(dialogForm, {
    id: row.id,
    title: row.title,
    teacher: row.teacher,
    category: row.category,
    image: row.image,
    resume: row.resume,
    content: row.content
  })
  dialogVisible.value = true
}

// 查看详情
const handleView = (row: any) => {
  viewData.value = { ...row }
  viewDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const url = dialogForm.id ? '/dev-api/yjnb/graphicCourse' : '/dev-api/yjnb/graphicCourse'
        const method = dialogForm.id ? 'put' : 'post'
        const res: any = await request[method](url, dialogForm)
        
        if (res.code === 200) {
          ElMessage.success(res.msg || '操作成功')
          dialogVisible.value = false
          getList()
        } else {
          ElMessage.error(res.msg || '操作失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error('提交失败')
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除课程${row.title}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res: any = await request.delete(`/dev-api/yjnb/graphicCourse/${row.id}`)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        getList()
      } else {
        ElMessage.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 切换推荐状态
const toggleRecommend = async (row: any) => {
  try {
    const apiUrl = row.recommend === 1 
      ? '/dev-api/yjnb/graphicCourse/recommend'
      : '/dev-api/yjnb/graphicCourse/unrecommend'
    
    const res: any = await request.post(apiUrl, [row.id])
    
    if (res.code === 200) {
      ElMessage.success(res.msg || '操作成功')
      getList()
    } else {
      ElMessage.error(res.msg || '操作失败')
      row.recommend = row.recommend === 1 ? 0 : 1 // 恢复状态
    }
  } catch (error) {
    console.error('切换推荐状态失败', error)
    ElMessage.error('切换推荐状态失败')
    row.recommend = row.recommend === 1 ? 0 : 1 // 恢复状态
  }
}

// 发布/取消发布
const handlePublish = (row: any) => {
  const action = row.publishStatus === 1 ? '取消发布' : '发布'
  ElMessageBox.confirm(`确定要${action}课程"${row.title}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const apiUrl = row.publishStatus === 1
        ? '/dev-api/yjnb/graphicCourse/unpublish'
        : '/dev-api/yjnb/graphicCourse/publish'
      
      const res: any = await request.post(apiUrl, [row.id])
      
      if (res.code === 200) {
        ElMessage.success(res.msg || `${action}成功`)
        getList()
      } else {
        ElMessage.error(res.msg || `${action}失败`)
      }
    } catch (error) {
      console.error(`${action}失败:`, error)
      ElMessage.error(`${action}失败`)
    }
  }).catch(() => {})
}

const handleImageUpload = async (file: any) => {
  if (!file.raw) return

  try {
    const result = await uploadImage(file.raw)
    dialogForm.image = result.url
    ElMessage.success('封面上传成功')
  } catch (error: any) {
    console.error('封面上传失败:', error)
    ElMessage.error(error?.message || '封面上传失败')
  }
}

// 导出
const handleExport = () => {
  exportCsv('图文课程列表', [
    { title: '课程标题', key: 'title' },
    { title: '讲师', key: 'teacher' },
    { title: '分类', key: 'category' },
    { title: '封面', key: 'image' },
    { title: '浏览数', key: 'browseNum' },
    { title: '发布状态', key: 'publishStatus' },
    { title: '推荐状态', key: 'recommend' },
    { title: '创建时间', key: 'createTime' },
  ], courseList.value)
  ElMessage.success('导出成功')
}

// 初始化
onMounted(() => {
  getList()
})
  </script>

<style scoped>
.graphic-course {
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
}

/* 页面标题 */
.page-header {
  background: white;
  padding: 20px 30px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 2px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(212, 165, 116, 0.2);
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
  font-size: 20px;
  font-weight: 600;
  color: #5a4a3a;
}

/* 搜索区域 */
.search-section {
  background: #fff;
  padding: 20px;
  border-radius: 0;
  margin: 20px 40px;
  border: 1px solid #e8e8e8;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.search-form :deep(.el-select) {
  width: 170px;
}

/* 快捷筛选标题*/
.filter-tags {
  margin: 0 40px 16px 40px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.filter-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(133, 185, 70, 0.3);
}

/* 工具题*/
.toolbar {
  margin: 0 40px 16px 40px;
  display: flex;
  gap: 10px;
}

/* 表格 */
.el-table {
  margin: 0 40px 20px 40px;
  border: 1px solid #e8e8e8;
  border-radius: 0;
  overflow: hidden;
  width: calc(100% - 80px) !important;
}

:deep(.el-table thead) {
  background: linear-gradient(to bottom, #1890ff 0%, #40a9ff 100%);
  color: #fff;
}

:deep(.el-table th) {
  background: transparent;
  color: #fff;
  font-weight: 600;
  border-color: rgba(255, 255, 255, 0.2);
}

:deep(.el-table td) {
  border-color: #e8e8e8;
}

:deep(.el-table tbody tr:hover > td) {
  background-color: #f0f2f5 !important;
}

.table-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  cursor: pointer;
}

/* 操作按钮 */
.action-btns {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btns .el-button {
  min-width: 70px;
}

/* 分页 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 对话框*/
:deep(.el-dialog) {
  border-radius: 12px;
  border: 2px solid #e8e8e8;
}

:deep(.el-dialog__header) {
  background: linear-gradient(to bottom, #f0f2f5 0%, #fff 100%);
  border-bottom: 1px solid #e8e8e8;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: #5a4a3a;
  font-weight: 600;
}

.preview-image {
  width: 200px;
  margin-top: 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.upload-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  width: 100%;
}

.cover-uploader {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  flex: 0 0 auto;
}

.cover-uploader:hover {
  border-color: #1890ff;
}

.cover-preview {
  width: 120px;
  height: 120px;
  object-fit: cover;
  display: block;
}

.upload-icon {
  width: 120px;
  height: 120px;
  font-size: 28px;
  color: #8c939d;
}

.upload-inputs {
  flex: 1;
  min-width: 0;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: #1890ff;
  border-color: #1890ff;
}

:deep(.el-button--primary:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
}
</style>
