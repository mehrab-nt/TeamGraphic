<template>
  <div class="min-h-screen flex center">
    <form @submit.prevent="onSubmit">
      <input v-model="phone" placeholder="شماره موبایل" />
      <input v-model="pass" type="password" placeholder="رمز عبور" />
      <button type="submit">Login</button>
      <p v-if="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

const phone = ref('')
const pass = ref('')
const error = ref(null)
const { login } = useAuth()

const onSubmit = async () => {
  try {
    await login({ phone_number: phone.value, password: pass.value })
  } catch (e) {
    error.value = 'Login failed'
  }
}
</script>
