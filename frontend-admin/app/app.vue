<template>
  <div>
    <NuxtLayout />
    <NuxtPage />
  </div>
</template>

<script setup>
const ready = ref(false)

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token || window.location.pathname === '/login') {
    ready.value = true
  } else {
    // Don't render anything until middleware kicks in
    navigateTo('/login')
  }
})
</script>
