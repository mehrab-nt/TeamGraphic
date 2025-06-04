// middleware/auth.js

export default defineNuxtRouteMiddleware((to, from) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return navigateTo('/login')  // Redirect to login page if not authenticated
  }
})