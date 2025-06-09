export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ]
    }
  },
  // Enable CORS-friendly SSR mode
  ssr: true, // default in Nuxt 3
  // Optional: runtime config for API base URL (used in useFetch, etc.)
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api/'
    }
  }
})
