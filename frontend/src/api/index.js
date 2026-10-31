import request from './request'

// ---------- 认证 ----------
export const registerApi = (data) => request.post('/auth/register', data)

export const loginApi = (username, password) => {
  // OAuth2PasswordRequestForm 要求 application/x-www-form-urlencoded
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  return request.post('/auth/login', form)
}

export const getMeApi = () => request.get('/auth/me')

// ---------- 工单 ----------
export const listTicketsApi = (params) => request.get('/tickets', { params })

export const createTicketApi = (data) => request.post('/tickets', data)

export const getTicketApi = (id) => request.get(`/tickets/${id}`)

export const replyTicketApi = (id, content) =>
  request.post(`/tickets/${id}/replies`, { content })

export const changeStatusApi = (id, status) =>
  request.patch(`/tickets/${id}/status`, { status })

// ---------- 图片上传 ----------
export const uploadImageApi = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/uploads', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
