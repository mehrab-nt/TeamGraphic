import { useAuth } from '../composables/useAuth'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { user, loading } = useAuth()

  // Wait until loading completes before redirecting
  while (loading.value) {
    await new Promise(r => setTimeout(r, 50))
  }

  if (to.path === '/login' && user.value) {
    return navigateTo('/dashboard')
  }

  if (to.path !== '/login' && !user.value) {
    return navigateTo('/login')
  }
})
