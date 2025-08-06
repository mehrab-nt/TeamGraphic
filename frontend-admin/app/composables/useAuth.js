import { useState } from '#imports'
import { useRouter } from 'vue-router'

export const useAuth = () => {
    const user = useState('authUser', () => null)
    const router = useRouter()

    const loadUser = () => {
        if (process.client) {
            const local_raw = localStorage.getItem('user')
            if (!local_raw) {
                const session_raw = sessionStorage.getItem('user')
                user.value = session_raw ? JSON.parse(session_raw) : null
            } else user.value = local_raw ? JSON.parse(local_raw) : null
        }
    }

    const login = async ({ phone_number, password, keep_me_signed_in }) => {
        const config = useRuntimeConfig()
        const res = await $fetch(`${config.public.apiBase}user/sign-in-with-password/`, {
            method: 'POST',
            body: { phone_number, password, keep_me_signed_in },
        })
        if (res.access && res.user) {
            if (keep_me_signed_in) {
                localStorage.setItem('access_token', res.access)
                localStorage.setItem('refresh_token', res.refresh)
                localStorage.setItem('user', JSON.stringify(res.user))
            } else {
                sessionStorage.setItem('access_token', res.access)
                sessionStorage.setItem('refresh_token', res.refresh)
                sessionStorage.setItem('user', JSON.stringify(res.user))
            }
            user.value = res.user
            await router.push('/dashboard')
        }
    }

    const logout = async () => {
        const local_refresh = process.client ? localStorage.getItem('refresh_token') : null
        let session_refresh
        if (!local_refresh) session_refresh = process.client ? sessionStorage.getItem('refresh_token') : null

        const config = useRuntimeConfig()
        if (local_refresh || session_refresh) {
            try {
                await $fetch(`${config.public.apiBase}user/sign-out-request/`, {
                    method: 'POST',
                    body: { refresh: local_refresh ? local_refresh : session_refresh },
                    headers: {
                        Authorization: `Bearer ${getAccessToken()}`,
                    },
                })
            } catch (e) {
                console.warn('Logout failed', e)
            }
        }
        user.value = null
        if (process.client){
            localStorage.clear()
            sessionStorage.clear()
        }
        await router.push('/login')
    }

    const getAccessToken = () => {
        let token = process.client ? localStorage.getItem('access_token') : null
        if (!token) token = process.client ? sessionStorage.getItem('access_token') : null
        return token
    }

    const refreshToken = async () => {
        if (!process.client) return false
        let local_token, session_token
        local_token = localStorage.getItem('refresh_token')
        if (!local_token) {
            session_token = sessionStorage.getItem('refresh_token')
            if (!session_token) return false
        }
        const config = useRuntimeConfig()
        try {
            const res = await $fetch(`${config.public.apiBase}token/refresh/`, {
                method: 'POST',
                body: { refresh: local_token ? local_token : session_token },
            })
            if (res.access) {
                local_token ? localStorage.setItem('access_token', res.access) : sessionStorage.setItem('access_token', res.access)
                return true
            }
            return false
        } catch {
            return false
        }
    }

    return { user, loadUser, login, logout, getAccessToken, refreshToken }
}
