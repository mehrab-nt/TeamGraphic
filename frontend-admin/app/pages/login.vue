<template>
  <div class="min-h-screen flex center">
    <form @submit.prevent="onSubmit">
      <input v-model="phone" placeholder="شماره موبایل" />
      <input v-model="pass" type="password" placeholder="رمز عبور" />
      <input v-model="keep" type="radio">
      <button type="submit">Login</button>
      <p v-if="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth.ts'

const phone = ref('')
const pass = ref('')
const keep = ref(false)
const error = ref(null)
const { login } = useAuth()

const onSubmit = async () => {
  try {
    await login( phone.value, pass.value, keep.value )
    error.value = null
  } catch (e:any) {
    if (e.data.detail) {
      error.value = e.data.detail
    } else if (e.detail) {
      error.value = e.detail
    } else if (e.data) {
      error.value = Object.values(e.data).flat().join(' | ')
    } else {
      error.value = 'خطای ناشناخته'
    }
  }
}
</script>
