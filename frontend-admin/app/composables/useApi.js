import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const loading = ref(true)
const error = ref(null)

export function useAuth() {
    const router = useRouter()
    const isClient = process.client

    const loadUser = () => {
        if (!isClient) return
        const storedUser = localStorage.getItem('user')
        if (storedUser) user.value = JSON.parse(storedUser)
        loading.value = false
    }

    const saveUser = (userData) => {
        user.value = userData
        if (isClient) {
            localStorage.setItem('user', JSON.stringify(userData))
        }
    }

    const clearAuth = () => {
        user.value = null
        if (isClient) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
        }
    }

    const login = async ({ phone_number, password }) => {
        error.value = null
        try {
            const config = useRuntimeConfig()
            const res = await $fetch(`${config.public.apiBase}user/sign-in-with-password/`, {
                method: 'POST',
                body: { phone_number, password, keep_me_signed_in: false },
            })
            if (res.access && res.user) {
                localStorage.setItem('access_token', res.access)
                localStorage.setItem('refresh_token', res.refresh)
                saveUser(res.user)
                await router.push('/dashboard')
            } else {
                error.value = 'توکن دریافت نشد.'
            }
        } catch (e) {
            error.value = e?.data?.detail || 'خطا در ورود. لطفاً دوباره تلاش کنید.'
        }
    }

    const logout = async () => {
        clearAuth()
        await router.push('/login')
    }

    // Run loadUser only on client mount
    if (isClient) {
        onMounted(() => loadUser())
    } else {
        loading.value = false // no user on server
    }

    return { user, loading, error, login, logout, clearAuth }
}
