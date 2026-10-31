import { defineStore } from 'pinia'
import { getMeApi, loginApi, registerApi } from '../api'

const TOKEN_KEY = 'ticket_token'
const USER_KEY = 'ticket_user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
  }),

  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    setAuth({ access_token, user }) {
      this.token = access_token
      this.user = user
      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },

    async login(username, password) {
      const res = await loginApi(username, password)
      this.setAuth(res)
    },

    async register(username, password) {
      const res = await registerApi({ username, password })
      this.setAuth(res)
    },

    async fetchMe() {
      this.user = await getMeApi()
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },

    clearAuth() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },

    logout() {
      this.clearAuth()
    },
  },
})
