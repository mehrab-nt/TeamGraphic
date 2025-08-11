<template>
  <div v-if="loading" class="min-h-screen flex items-center justify-center">
    <p>Loading...</p>
  </div>
  <NuxtLayout v-else>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth.ts'
import { ref, onMounted } from 'vue'
const { user, loadUser } = useAuth()
const loading = ref(true)

onMounted(() => {
  loadUser()
  loading.value = false
})
</script>
