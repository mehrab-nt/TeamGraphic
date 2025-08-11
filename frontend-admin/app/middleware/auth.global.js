// app/middleware/auth.global.js
import { useAuth } from '~/composables/useAuth.ts'

export default defineNuxtRouteMiddleware(async (to) => {
    const { user, loadUser } = useAuth()
    if (process.client && !user.value) loadUser()

    if (to.path === '/login' && user.value) return navigateTo('/dashboard')
    if (to.path !== '/login' && !user.value) return navigateTo('/login')
})
