<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="always">
      <div class="brand">
        <el-icon :size="30" color="#409eff"><Tools /></el-icon>
        <h2>工单报修管理系统</h2>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="请输入密码"
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="handleLogin">
          登 录
        </el-button>
      </el-form>

      <div class="footer">
        没有账号？<router-link to="/register">立即注册</router-link>
      </div>
      <div class="tip">默认管理员账号：admin / admin123</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.username.trim(), form.password)
    ElMessage.success('登录成功')
    router.push('/tickets')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f4e8c 0%, #409eff 100%);
}
.auth-card {
  width: 400px;
  padding: 20px 24px 12px;
  border-radius: 10px;
}
.brand {
  text-align: center;
  margin-bottom: 24px;
}
.brand h2 {
  margin: 10px 0 0;
  color: #303133;
  font-size: 20px;
}
.submit {
  width: 100%;
}
.footer {
  text-align: center;
  margin-top: 14px;
  color: #606266;
  font-size: 14px;
}
.tip {
  text-align: center;
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
