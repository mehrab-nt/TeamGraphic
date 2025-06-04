<script setup>
import axios from "axios";
const { data, error, pending } = useAsyncData('user-list', async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/user')
    return response.data
  }
  catch (err) {
    console.error(err)
    throw new Error('Error fetching user data')
  }
})
</script>

<template>
  <div>
    <h1>User List</h1>
    <div v-if="pending">Loading...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <ul v-else>
      <li v-for="user in data" :key="user.id" class="mb-2">
        {{ user.phone_number }}
      </li>
    </ul>
  </div>
</template>
