<template>
  <div v-loading="loading">
    <el-page-header @back="router.push('/tickets')" class="page-header">
      <template #content>
        <span class="header-title">工单详情</span>
      </template>
    </el-page-header>

    <template v-if="detail">
      <!-- 工单信息 -->
      <el-card shadow="never" class="block">
        <template #header>
          <div class="ticket-header">
            <span class="ticket-title">#{{ detail.id }} {{ detail.title }}</span>
            <el-tag :type="STATUS_MAP[detail.status]?.type" size="large">
              {{ STATUS_MAP[detail.status]?.label }}
            </el-tag>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="报修人">{{ detail.author_name }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="最近更新">{{ formatTime(detail.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="问题描述" :span="3">
            <div class="description">{{ detail.description }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="现场图片" :span="3">
            <el-image
              v-if="detail.image_url"
              :src="detail.image_url"
              fit="cover"
              class="ticket-image"
              :preview-src-list="[detail.image_url]"
              preview-teleported
            />
            <span v-else class="muted">未上传图片</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 状态进度条 -->
        <el-steps :active="statusIndex" align-center finish-status="success" class="steps">
          <el-step title="待处理" />
          <el-step title="处理中" />
          <el-step title="已完成" />
        </el-steps>
      </el-card>

      <!-- 管理员处理区 -->
      <el-card v-if="userStore.isAdmin" shadow="never" class="block">
        <template #header>
          <span class="card-title">处理工单</span>
        </template>
        <div v-if="nextStatusOptions.length" class="status-action">
          <span>变更状态：</span>
          <el-select v-model="nextStatus" placeholder="选择目标状态" style="width: 160px">
            <el-option
              v-for="opt in nextStatusOptions"
              :key="opt"
              :value="opt"
              :label="STATUS_MAP[opt]?.label"
            />
          </el-select>
          <el-button type="primary" :loading="statusLoading" @click="handleChangeStatus">
            确认变更
          </el-button>
          <span class="muted">仅允许 待处理 → 处理中 → 已完成 向前流转</span>
        </div>
        <el-alert v-else title="工单已完结" type="success" :closable="false" show-icon />
      </el-card>

      <!-- 回复区 -->
      <el-card shadow="never" class="block">
        <template #header>
          <span class="card-title">处理沟通（{{ detail.replies.length }}）</span>
        </template>

        <el-timeline v-if="detail.replies.length">
          <el-timeline-item
            v-for="r in detail.replies"
            :key="r.id"
            :timestamp="formatTime(r.created_at)"
            placement="top"
          >
            <el-card shadow="hover" class="reply-card">
              <div class="reply-head">
                <span class="reply-author">{{ r.author_name }}</span>
                <el-tag size="small" :type="r.author_role === 'admin' ? 'danger' : 'info'">
                  {{ r.author_role === 'admin' ? '管理员' : '报修人' }}
                </el-tag>
              </div>
              <div class="reply-content">{{ r.content }}</div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无沟通记录" :image-size="80" />

        <div class="reply-box">
          <el-input
            v-model="replyContent"
            type="textarea"
            :rows="3"
            maxlength="1000"
            show-word-limit
            :placeholder="userStore.isAdmin ? '填写处理方案或进展说明…' : '补充问题信息或确认处理结果…'"
          />
          <el-button type="primary" :loading="replyLoading" class="reply-btn" @click="handleReply">
            发送回复
          </el-button>
        </div>
      </el-card>

      <!-- 操作日志（管理员可见） -->
      <el-card v-if="userStore.isAdmin" shadow="never" class="block">
        <template #header>
          <span class="card-title">操作日志</span>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="log in detail.logs"
            :key="log.id"
            :timestamp="formatTime(log.created_at)"
            placement="top"
            :type="log.action === 'status_change' ? 'primary' : undefined"
          >
            <span class="log-operator">{{ log.operator_name }}</span>
            <el-tag size="small" class="log-tag">{{ ACTION_MAP[log.action] || log.action }}</el-tag>
            <span v-if="log.detail" class="log-detail">{{ log.detail }}</span>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTicketApi, replyTicketApi, changeStatusApi } from '../api'
import { useUserStore } from '../stores/user'
import { STATUS_MAP, ALLOWED_TRANSITIONS, ACTION_MAP } from '../utils/constants'
import { formatTime } from '../utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const detail = ref(null)
const replyContent = ref('')
const replyLoading = ref(false)
const nextStatus = ref('')
const statusLoading = ref(false)

const statusIndex = computed(() => {
  const order = ['pending', 'processing', 'completed']
  return detail.value ? order.indexOf(detail.value.status) : 0
})

// 依据状态机给出当前可流转到的状态
const nextStatusOptions = computed(() =>
  detail.value ? ALLOWED_TRANSITIONS[detail.value.status] || [] : []
)

async function fetchDetail() {
  loading.value = true
  try {
    detail.value = await getTicketApi(route.params.id)
    nextStatus.value = nextStatusOptions.value[0] || ''
  } finally {
    loading.value = false
  }
}

async function handleChangeStatus() {
  if (!nextStatus.value) return
  const label = STATUS_MAP[nextStatus.value]?.label
  await ElMessageBox.confirm(`确定将工单状态变更为「${label}」吗？`, '状态变更', {
    type: 'warning',
  })
  statusLoading.value = true
  try {
    await changeStatusApi(detail.value.id, nextStatus.value)
    ElMessage.success('状态已更新')
    await fetchDetail()
  } finally {
    statusLoading.value = false
  }
}

async function handleReply() {
  const content = replyContent.value.trim()
  if (!content) {
    ElMessage.warning('请输入回复内容')
    return
  }
  replyLoading.value = true
  try {
    await replyTicketApi(detail.value.id, content)
    replyContent.value = ''
    ElMessage.success('回复成功')
    await fetchDetail()
  } finally {
    replyLoading.value = false
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}
.header-title {
  font-weight: 600;
}
.block {
  margin-bottom: 16px;
}
.card-title {
  font-weight: 600;
}
.ticket-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ticket-title {
  font-size: 16px;
  font-weight: 600;
}
.description {
  white-space: pre-wrap;
  line-height: 1.7;
}
.ticket-image {
  width: 220px;
  height: 160px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}
.muted {
  color: #909399;
}
.steps {
  margin-top: 24px;
}
.status-action {
  display: flex;
  align-items: center;
  gap: 10px;
}
.reply-card {
  margin-bottom: 2px;
}
.reply-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.reply-author {
  font-weight: 600;
  color: #303133;
}
.reply-content {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #303133;
}
.reply-box {
  margin-top: 16px;
}
.reply-btn {
  margin-top: 10px;
}
.log-operator {
  font-weight: 600;
  margin-right: 8px;
}
.log-tag {
  margin-right: 8px;
}
.log-detail {
  color: #606266;
}
</style>
