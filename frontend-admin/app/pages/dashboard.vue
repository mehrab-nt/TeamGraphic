<script setup>
import { useAuth } from '~/composables/useAuth'
const { user, loadUser, logout } = useAuth()

onMounted(() => {
  loadUser()
})
</script>

<template>
  <div v-if="!user">
    Loading...
  </div>
  <div v-else>
    Welcome, {{ user.id }}<button @click="logout">Logout</button>
  </div>
</template>
