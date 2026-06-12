<!-- <template>
    <div>
      <el-icon :size="40" color="red">
        <Edit />
      </el-icon>
    </div>
  </template>

<script setup>
    import { Edit } from '@element-plus/icons-vue'
</script> -->


<template>
  <div style="padding: 20px;">
    <h4>请选择一个选项：</h4>
    <el-select v-model="selected" placeholder="请选择">
      <el-option
        v-for="item in options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
      >
        {{ item.label }} - {{ item.extra }}
      </el-option>
    </el-select>

  </div>
</template>

<script setup>
import { ref } from 'vue'
// 如果你已全局引入 Element Plus，则不需要单独导入组件
const selected = ref('')
const options = [
  { label: '北京', value: 'bj', extra: '首都' },
  { label: '上海', value: 'sh', extra: '直辖市' },
  { label: '广州', value: 'gz', extra: '一线城市' }
]
</script>