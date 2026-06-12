<template>
    <div class="common-layout">
      <el-container>
       <el-header><nav-header></nav-header></el-header>
       <el-container>
        <el-aside width="180px"><side-menu></side-menu></el-aside>
        <el-main><router-view></router-view></el-main>
        <!-- <el-main><Konwladge></Konwladge></el-main> -->
       </el-container>
      </el-container>
    </div>
</template>
    
<script lang="ts" setup> 
    // import Konwladge from './views/konwladge.vue';
</script>
    
<style scoped>   
    .common-layout,.el-container{
        height: 100vh;
        width: 100%;
        background: #f0f2f5;
     } 
    .el-header{
        padding: 0;
        height: 60px; 
        width:100%;
        background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .el-aside {
        background: #ffffff;
        border-right: 1px solid #e8e8e8;
    }
    
    .el-main {
        padding: 0;
        background: #f0f2f5;
    }
</style>

