<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <form @submit.prevent="onSubmit" class="bg-white p-8 rounded shadow-md w-full max-w-sm space-y-4">
      <h2 class="text-xl font-bold text-center">Admin Login</h2>
      <input v-model="phone_number" placeholder="شماره موبایل" required class="input" />
      <input v-model="password" type="password" placeholder="رمز عبور" required class="input" />
      <button type="submit" class="btn w-full" :disabled="loading">Login</button>
      <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

const phone_number = ref('')
const password = ref('')
const { login, error, loading } = useAuth()

const onSubmit = async () => {
  await login({ phone_number: phone_number.value, password: password.value })
}
</script>

<style scoped>
.input {
  @apply w-full p-2 border border-gray-300 rounded;
}
.btn {
  @apply bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50;
}
</style>
