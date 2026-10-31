<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="always">
      <div class="brand">
        <el-icon :size="30" color="#67c23a"><Tools /></el-icon>
        <h2>注册新账号</h2>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="用户名（3-20 位）" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="密码（6-32 位）"
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item prop="confirm">
          <el-input
            v-model="form.confirm"
            size="large"
            type="password"
            show-password
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-button type="success" size="large" class="submit" :loading="loading" @click="handleRegister">
          注 册
        </el-button>
      </el-form>

      <div class="footer">
        已有账号？<router-link to="/login">返回登录</router-link>
      </div>
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
const form = reactive({ username: '', password: '', confirm: '' })

const validateConfirm = (_rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度为 6-32 位', trigger: 'blur' },
  ],
  confirm: [{ validator: validateConfirm, trigger: 'blur' }],
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    // 注册成功后自动登录
    await userStore.register(form.username.trim(), form.password)
    ElMessage.success('注册成功，已自动登录')
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
</style>
