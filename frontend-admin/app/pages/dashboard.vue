<template>
  <div v-if="loading" class="flex items-center justify-center min-h-screen">
    <div>Loading...</div>
  </div>
  <div v-else>
    <nav class="p-4 bg-gray-200 flex justify-between">
      <h1>Dashboard</h1>
      <button @click="logout" class="btn">Logout</button>
    </nav>
    <main class="p-4">
      <h2>Welcome, user {{ user?.id }}</h2>
      <!-- Your dashboard content here -->
    </main>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth'
const { user, loading, logout } = useAuth()
</script>

<style scoped>
.btn {
  @apply bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700;
}
</style>
