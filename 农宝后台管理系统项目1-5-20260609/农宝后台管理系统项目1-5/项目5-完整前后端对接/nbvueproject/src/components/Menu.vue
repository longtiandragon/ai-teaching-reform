<template>
    <el-menu
        default-active="/main/system"
        router
        @open="handleOpen"
        @close="handleClose"
    >
        <el-menu-item index="/main/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>数据大屏</span>
        </el-menu-item>
        <el-menu-item index="/main/system">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
        </el-menu-item>
        <el-menu-item index="/main/advertisement">
            <el-icon><IconMenu /></el-icon>
            <span>广告管理</span>
        </el-menu-item>
        <el-menu-item index="/main/policy">
            <el-icon><document /></el-icon>
            <span>补贴政策</span>
        </el-menu-item>
        <el-menu-item index="/main/konwladge/index">
            <el-icon><Box /></el-icon>
            <span>知识管理</span>
        </el-menu-item>
        <el-menu-item index="/main/service">  
            <el-icon><Van /></el-icon>
            <span>农事服务</span>
        </el-menu-item>
        <el-menu-item index="/main/market">  
            <el-icon><Comment /></el-icon>
            <span>农贸市场</span>
        </el-menu-item>
        <el-menu-item index="/main/loan">
            <el-icon><MessageBox /></el-icon>
            <span>信贷管理</span>
        </el-menu-item>
        <el-menu-item index="/main/produce">
            <el-icon><Notification /></el-icon>
            <span>农产品管理</span>
        </el-menu-item>
    </el-menu>
</template>
     
<script lang="ts" setup>
    import {
        Setting,
        Menu as IconMenu,
        Document,
        Box,
        Comment,
        MessageBox,
        Notification,
        Van,
        DataAnalysis,
        DataBoard
    } from '@element-plus/icons-vue'
    const handleOpen = (key: string, keyPath: string[]) => {
        console.log(key, keyPath)
    }
    const handleClose = (key: string, keyPath: string[]) => {
        console.log(key, keyPath)
    }
 </script>

 <style scoped>
    .el-menu{
        height: 100%;
        background: #ffffff;
        border-right: 1px solid #e8e8e8;
    }
    
    :deep(.el-menu-item) {
        color: #333;
        font-size: 14px;
        transition: all 0.3s;
        padding-left: 20px !important;
    }
    
    :deep(.el-menu-item:hover) {
        background-color: #e6f7ff !important;
        color: #1890ff;
    }
    
    :deep(.el-menu-item.is-active) {
        background-color: #1890ff !important;
        color: white !important;
        border-right: 3px solid #096dd9;
    }
    
    :deep(.el-menu-item .el-icon) {
        color: inherit;
        margin-right: 8px;
    }
</style>