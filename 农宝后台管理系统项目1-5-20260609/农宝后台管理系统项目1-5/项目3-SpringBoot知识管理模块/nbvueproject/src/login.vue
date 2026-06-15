<template>
	<div class="bg">
		<form action="#">
			<table cellspacing=10>			
				<tr height=40px><td align="center">农宝管理系统</td></tr>
				<tr height=40px><td><input type="text" placeholder="请输入用户名" v-model="username" required/></td></tr>
				<tr height=40px><td><input type="password" placeholder="请输入密码" v-model="password" required/></td></tr>
				<tr height=40px><td><button type="button" @click="login">登录</button></td></tr>
			</table>
		</form>
	</div>
</template>

<script lang="ts" setup>
	import { ref } from 'vue'
	import { useRouter } from 'vue-router'
	import { useUserStore } from './store/user'
	
	const router = useRouter()
	const userStore = useUserStore()
	
	const username = ref('')
	const password = ref('')
	
	const login = async () => {
		// 调用 Pinia store 的智能登录方法
		// 会自动尝试API登录,失败时降级到本地验证
		const result = await userStore.login(username.value, password.value)
		
		if (result.success) {
			router.push('/main')
		} else {
			alert(result.message || "登录失败")
		}
	}
</script>

<style scoped>
	.bg {
		background-image: url('./assets/images/login-bg.png');
		background-size: cover; /* 让背景图片根据容器大小进行缩放 */
		background-position: center; /* 确保背景图居中 */
		width: 100vw; /* 使用视窗单位让宽度占满整个屏幕 */
		height: 100vh; /* 使用视窗单位让高度占满整个屏幕 */
		position: fixed; /* 固定定位 */
		top: 0;
		left: 0;
	}
	table{
		margin: 120px auto;
		padding: 40px 40px;
		background-color: white;
	}
	button{
		width: 305px;
		height: 50px;
		color: white;
		background-color: rgb(64, 158, 255);
		border-radius: 5px;
		border: none;
	}
	input{
		width:300px;
		height: 40px;
	}
</style>
