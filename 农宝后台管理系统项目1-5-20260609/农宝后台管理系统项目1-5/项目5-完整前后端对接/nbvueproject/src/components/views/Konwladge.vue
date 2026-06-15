<template>
  <div class="knowledge-container">
    <el-tabs v-model="activeTab" type="card" class="knowledge-tabs">
      <el-tab-pane label="专家列表" name="tab-one">
        <ExpertList />
      </el-tab-pane>
      <el-tab-pane label="图文课程" name="tab-two">
        <GraphicCourse />
      </el-tab-pane>
      <el-tab-pane label="视频课程" name="tab-three">
        <VideoCourse />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ExpertList from './ExpertList.vue';
import GraphicCourse from './GraphicCourse.vue';
import VideoCourse from './VideoCourse.vue';

const activeTab = ref('tab-one'); // 默认激活的 Tab
</script>

<style scoped>
.knowledge-container {
  width: 100%;
  height: 100%;
  background: #fff;
  overflow: auto;
}

.knowledge-tabs {
  width: 100%;
}

:deep(.el-tabs__header) {
  margin: 0;
  background: #fff;
  padding: 10px 20px 0;
}

:deep(.el-tabs__content) {
  padding: 0;
  width: 100%;
  overflow: visible;
}

:deep(.el-tab-pane) {
  width: 100%;
}
</style>