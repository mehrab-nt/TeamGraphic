import { useAuth } from './useAuth'

export function useApi() {
    const { logout, getToken, refreshToken } = useAuth()
    const config = useRuntimeConfig()

    const fetchWithAuth = async (url, options = {}) => {
        if (!process.client) return { data: null, error: 'SSR' }

        options.headers = {
            ...(options.headers || {}),
            Authorization: `Bearer ${getToken()}`
        }

        try {
            const data = await $fetch(`${config.public.apiBase}${url}`, options)
            return { data, error: null }
        } catch (err) {
            if (err.response?.status === 401) {
                const ok = await refreshToken()
                if (ok) {
                    options.headers.Authorization = `Bearer ${getToken()}`
                    try {
                        const data = await $fetch(`${config.public.apiBase}${url}`, options)
                        return { data, error: null }
                    } catch {
                        await logout()
                    }
                } else {
                    await logout()
                }
            }
            return { data: null, error: err }
        }
    }

    return { fetchWithAuth }
}
