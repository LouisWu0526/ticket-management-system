<template>
  <div>
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <el-radio-group v-model="query.status" @change="handleFilterChange">
          <el-radio-button value="">全部状态</el-radio-button>
          <el-radio-button v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </el-radio-button>
        </el-radio-group>

        <div class="filter-right">
          <el-input
            v-model="query.keyword"
            placeholder="搜索工单标题"
            clearable
            style="width: 220px"
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="router.push('/tickets/create')">
            提交工单
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 工单表格 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <span class="card-title">{{ userStore.isAdmin ? '全部工单' : '我的工单' }}</span>
      </template>

      <el-table v-loading="loading" :data="list" border stripe style="width: 100%">
        <el-table-column prop="id" label="工单号" width="80" />
        <el-table-column label="标题" min-width="240">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">{{ row.title }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="STATUS_MAP[row.status]?.type">{{ STATUS_MAP[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isAdmin" prop="author_name" label="报修人" width="120" />
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">
              {{ userStore.isAdmin ? '处理' : '查看' }}
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无工单" />
        </template>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="fetchData"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import { listTicketsApi } from '../api'
import { useUserStore } from '../stores/user'
import { STATUS_MAP, STATUS_OPTIONS } from '../utils/constants'
import { formatTime } from '../utils/format'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ status: '', keyword: '', page: 1, page_size: 10 })

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.status) params.status = query.status
    if (query.keyword) params.keyword = query.keyword.trim()
    const res = await listTicketsApi(params)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  query.page = 1
  fetchData()
}

function handleSearch() {
  query.page = 1
  fetchData()
}

function handleReset() {
  query.status = ''
  query.keyword = ''
  query.page = 1
  fetchData()
}

function handleSizeChange() {
  query.page = 1
  fetchData()
}

function goDetail(id) {
  router.push(`/tickets/${id}`)
}

onMounted(fetchData)
</script>

<style scoped>
.filter-card {
  margin-bottom: 16px;
}
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.filter-right {
  display: flex;
  gap: 8px;
}
.card-title {
  font-weight: 600;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
