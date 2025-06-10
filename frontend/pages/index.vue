<script setup>
const { data, error, pending } = useAsyncData('user-list', async () => {
  try {
    const response = await useFetch('http://127.0.0.1:8000/api/users/')
    return response.data.value
  } catch (err) {
    console.error(err) // Log any error to get more details
    throw new Error('Error fetching user data')
  }
})
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">User List</h1>
    <div v-if="pending">Loading...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <ul v-else>
      <li v-for="user in data.results" :key="user.id" class="mb-2">
        {{ user }}
      </li>
    </ul>
  </div>
</template>