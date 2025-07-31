export default defineNuxtRouteMiddleware(async (to) => {
  const { user, loadUser } = useAuth()

  // Always hydrate user on client
  if (process.client && !user.value) {
    loadUser()
  }

  // If unauthenticated on a protected route
  if (to.path !== '/login' && !user.value) {
    return navigateTo('/login')
  }

  // If already authenticated and visiting login
  if (to.path === '/login' && user.value) {
    return navigateTo('/dashboard')
  }
})
