<template>
  <div class="image-upload-container">
    <el-upload
      class="image-uploader"
      :action="uploadUrl"
      :show-file-list="false"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :headers="headers"
      accept="image/*"
    >
      <img v-if="imageUrl" :src="imageUrl" class="preview-image" />
      <el-icon v-else class="uploader-icon"><Plus /></el-icon>
    </el-upload>
    <div class="upload-tips">
      <p>{{ tips }}</p>
      <el-input 
        v-model="imageUrl" 
        placeholder="或直接输入图片URL" 
        clearable
        size="small"
        style="margin-top: 8px;"
        @input="handleUrlChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
  tips?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  tips: '点击上传图片或输入图片URL'
})

const emit = defineEmits(['update:modelValue'])

const imageUrl = ref(props.modelValue)
const uploadUrl = ref('/dev-api/yjnb/upload/image')
const headers = ref({
  'Authorization': localStorage.getItem('token') || ''
})

watch(() => props.modelValue, (newVal) => {
  imageUrl.value = newVal
})

const handleUrlChange = () => {
  emit('update:modelValue', imageUrl.value)
}

const beforeUpload = (file: any) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

const handleSuccess = (response: any) => {
  if (response.code === 200) {
    imageUrl.value = response.data.url
    emit('update:modelValue', imageUrl.value)
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

const handleError = () => {
  ElMessage.error('上传失败，请重试')
}
</script>

<style scoped>
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
  background: #f0f9ff;
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
</style>

