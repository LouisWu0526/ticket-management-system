<template>
  <el-card shadow="never" class="form-card">
    <template #header>
      <span class="card-title">提交报修工单</span>
    </template>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" style="max-width: 720px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" maxlength="100" show-word-limit placeholder="简要描述问题，如：办公室空调不制冷" />
      </el-form-item>

      <el-form-item label="问题描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="6"
          maxlength="1000"
          show-word-limit
          placeholder="请详细描述故障现象、发生时间、地点等信息，便于维修人员处理"
        />
      </el-form-item>

      <el-form-item label="现场图片">
        <el-upload
          :show-file-list="false"
          :before-upload="beforeUpload"
          :http-request="handleUpload"
          accept="image/*"
        >
          <el-button :icon="Upload" :loading="uploading">
            {{ uploading ? '上传中...' : '选择图片' }}
          </el-button>
          <template #tip>
            <div class="upload-tip">支持 jpg/png/gif/webp，大小不超过 5MB，可选上传 1 张</div>
          </template>
        </el-upload>

        <div v-if="form.image_url" class="preview">
          <el-image
            :src="form.image_url"
            fit="cover"
            style="width: 180px; height: 180px; border-radius: 6px"
            :preview-src-list="[form.image_url]"
            preview-teleported
          />
          <el-button link type="danger" :icon="Delete" @click="form.image_url = ''">移除图片</el-button>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交工单</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, Delete } from '@element-plus/icons-vue'
import { createTicketApi, uploadImageApi } from '../api'

const router = useRouter()

const formRef = ref()
const submitting = ref(false)
const uploading = ref(false)
const form = reactive({ title: '', description: '', image_url: '' })

const rules = {
  title: [
    { required: true, message: '请输入工单标题', trigger: 'blur' },
    { max: 100, message: '标题不能超过 100 字', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { max: 1000, message: '描述不能超过 1000 字', trigger: 'blur' },
  ],
}

function beforeUpload(file) {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

async function handleUpload({ file }) {
  uploading.value = true
  try {
    const res = await uploadImageApi(file)
    form.image_url = res.url
    ElMessage.success('图片上传成功')
  } finally {
    uploading.value = false
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await createTicketApi({
      title: form.title.trim(),
      description: form.description.trim(),
      image_url: form.image_url || null,
    })
    ElMessage.success('工单提交成功，请等待管理员处理')
    router.push('/tickets')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-card {
  max-width: 900px;
}
.card-title {
  font-weight: 600;
}
.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
.preview {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}
</style>
