<template>
  <div>
    <nav>
      <button @click="logout">Logout</button>
    </nav>
    <h1>Welcome, {{ user.id }}</h1>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth'
const { user, logout } = useAuth()
</script>
