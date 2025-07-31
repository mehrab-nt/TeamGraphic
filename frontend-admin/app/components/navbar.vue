<script setup>
const router = useRouter()

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<template>
  <nav>
    <button @click="logout">Logout</button>
  </nav>
</template>
