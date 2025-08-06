import { useState } from '#imports'
import { useRouter } from 'vue-router'

export const useAuth = () => {
    const user = useState('authUser', () => null)
    const router = useRouter()

    const loadUser = () => {
        if (process.client) {
            const raw = localStorage.getItem('user')
            user.value = raw ? JSON.parse(raw) : null
        }
    }

    const login = async ({ phone_number, password, keep_me_signed_in }) => {
        const config = useRuntimeConfig()
        const res = await $fetch(`${config.public.apiBase}user/sign-in-with-password/`, {
            method: 'POST',
            body: { phone_number, password, keep_me_signed_in },
        })
        if (res.access && res.user) {
            localStorage.setItem('access_token', res.access)
            localStorage.setItem('refresh_token', res.refresh)
            localStorage.setItem('user', JSON.stringify(res.user))
            user.value = res.user
            await router.push('/dashboard')
        }
    }

    const logout = async () => {
        const refresh = process.client ? localStorage.getItem('refresh_token') : null
        const config = useRuntimeConfig()
        if (refresh) {
            try {
                await $fetch(`${config.public.apiBase}user/sign-out-request/`, {
                    method: 'POST',
                    body: { refresh },
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                })
            } catch (e) {
                console.warn('Logout failed', e)
            }
        }
        user.value = null
        if (process.client) localStorage.clear()
        await router.push('/login')
    }

    const getAccessToken = () => (process.client ? localStorage.getItem('access_token') : null)

    const refreshToken = async () => {
        if (!process.client) return false
        const token = localStorage.getItem('refresh_token')
        if (!token) return false

        const config = useRuntimeConfig()
        try {
            const res = await $fetch(`${config.public.apiBase}token/refresh/`, {
                method: 'POST',
                body: { refresh: token },
            })
            if (res.access) {
                localStorage.setItem('access_token', res.access)
                return true
            }
            return false
        } catch {
            return false
        }
    }

    return { user, loadUser, login, logout, getAccessToken, refreshToken }
}
