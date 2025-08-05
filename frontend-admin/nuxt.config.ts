export default defineNuxtConfig({
  vite: {
    server: {
      proxy: {
        // Proxy all /api requests to your Django backend
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api'),
        },
      },
    },
  },
  runtimeConfig: {
    public: {
      apiBase: '/api/', // use proxy, so relative URL works
    },
  },
})