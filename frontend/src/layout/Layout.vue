<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="22"><Tools /></el-icon>
        <span>工单报修系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
        background-color="#001529"
        text-color="#b7c0cd"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/tickets">
          <el-icon><Tickets /></el-icon>
          <span>{{ userStore.isAdmin ? '全部工单' : '我的工单' }}</span>
        </el-menu-item>
        <el-menu-item index="/tickets/create">
          <el-icon><Plus /></el-icon>
          <span>提交工单</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">工单报修管理系统</div>
        <div class="user-box">
          <el-icon><UserFilled /></el-icon>
          <span class="username">{{ userStore.user?.username }}</span>
          <el-tag size="small" :type="userStore.isAdmin ? 'danger' : 'info'">
            {{ userStore.isAdmin ? '管理员' : '普通用户' }}
          </el-tag>
          <el-button link type="primary" :icon="SwitchButton" @click="handleLogout">
            退出登录
          </el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

async function handleLogout() {
  await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100%;
}
.aside {
  background-color: #001529;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 1px;
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.user-box {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}
.username {
  font-weight: 500;
}
.main {
  padding: 20px;
}
</style>
