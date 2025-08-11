<template>
  <button @click="logout">Logout</button>
  <div>
    <h1>User List</h1>
    <p v-if="loading">Loading users...</p>
    <p v-if="error" style="color:red;">{{ error }}</p>
    <ul v-if="!loading && !error">
      <li v-for="user in users" :key="user.id">
        {{ user['phone_number'] }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const users = ref([])
const error = ref(null)
const loading = ref(false)

const { fetchWithAuth } = useApi()

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const res = await fetchWithAuth('user/')
    users.value = res.results || []
  } catch (e:any) {
    error.value = e.detail || e.message || 'Unknown error'
  } finally {
    loading.value = false
  }
})

import { useAuth } from '~/composables/useAuth'

const { logout } = useAuth()
</script>
