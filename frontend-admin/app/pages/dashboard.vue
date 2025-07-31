<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { useAuth } from '~/composables/useAuth'

const users = ref([])
const loading = ref(true)
const error = ref(null)

const { fetchWithAuth } = useApi()
const { logout } = useAuth()

const loadUsers = async () => {
  loading.value = true
  error.value = null
  const { data, error: err } = await fetchWithAuth('user/')
  if (err) {
    if (err?.response?.status === 401) {
      // Unauthorized: force logout
      await logout()
    } else {
      error.value = 'Failed to load users.'
      console.error('User fetch error:', err)
    }
  } else {
    users.value = data?.results || []
  }
  loading.value = false
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div>
    <h1>Users</h1>
    <div v-if="loading">Loading users...</div>
    <p v-else-if="error">{{ error }}</p>
    <ul v-else>
      <li v-for="user in users" :key="user.id">{{ user.phone_number }}</li>
    </ul>
  </div>
</template>
