<template>
    <el-row type="flex" justify="space-between" align="middle">
        <el-col :span="12">
            <img src="@/assets/images/zhunong.png" alt="logo"/>
            <span>助农APP管理运营后台</span>
        </el-col>
        <el-col :span="4" class="span user-area">
            <span class="user-name">{{ userStore.userInfo }}</span>
            <button v-if="userStore.isLoggedIn" @click="handleLogout" class="logout-btn">
                退出登录
            </button>
        </el-col>    
    </el-row>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

// 页面加载时检查登录状态
onMounted(() => {
    userStore.checkLogin()
})

// 退出登录
const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
        userStore.logout()  // 调用 Pinia store 的 logout 方法
        router.push('/login')  // 跳转到登录页
    }
}
</script>
    
<style scoped>
    .el-row{        
        width: 100%;
		height: 60px;
		background-color: rgb(27, 179, 245);
        padding: 0 25px; 
        color: white;
    }
    .el-row > .el-col:nth-of-type(2){
        text-align: right;
    }
    img {
        width: 50px;
        height: 50px;
        vertical-align: middle; /* 垂直居中对齐图片 */
        margin-right: 10px; /* 图片与文字之间留点空隙 */
    }

    .span {
        font-size: 12px;
    }
    
    .user-area {
        display: flex;
        align-items: center;
        gap: 15px;
        justify-content: flex-end;
    }
    
    .user-name {
        font-size: 14px;
    }
    
    .logout-btn {
        padding: 5px 15px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.3s;
    }
    
    .logout-btn:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border-color: white;
    }
</style>