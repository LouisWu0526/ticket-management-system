// 工单状态展示配置（与后端状态枚举保持一致）
export const STATUS_MAP = {
  pending: { label: '待处理', type: 'info' },
  processing: { label: '处理中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
}

export const STATUS_OPTIONS = [
  { value: 'pending', label: '待处理' },
  { value: 'processing', label: '处理中' },
  { value: 'completed', label: '已完成' },
]

// 允许的状态流转（与后端 ALLOWED_TRANSITIONS 对应，仅用于前端控制可选项）
export const ALLOWED_TRANSITIONS = {
  pending: ['processing', 'completed'],
  processing: ['completed'],
  completed: [],
}

// 操作日志动作中文映射
export const ACTION_MAP = {
  create: '提交工单',
  status_change: '状态变更',
  reply: '回复工单',
}

export const ROLE_MAP = {
  user: '普通用户',
  admin: '管理员',
}

export function statusLabel(status) {
  return STATUS_MAP[status]?.label || status
}
