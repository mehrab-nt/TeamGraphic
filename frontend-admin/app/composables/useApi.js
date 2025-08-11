import { useAuth } from './useAuth'

export function useApi() {
    const { getAccessToken, refreshToken, logout } = useAuth()

    async function fetchWithAuth(url, options = {}) {
        let token = getAccessToken()

        if (!token) {
            // No access token at all
            throw new Error('No access token found. Please login.')
        }

        if (!options.headers) options.headers = {}
        options.headers.Authorization = `Bearer ${token}`

        const config = useRuntimeConfig()
        let res = await fetch(config.public.apiBase + url, options)

        if (res.status === 401) {
            // Try to refresh token once
            const refreshed = await refreshToken()
            if (refreshed) {
                token = getAccessToken()
                options.headers.Authorization = `Bearer ${token}`
                res = await fetch(config.public.apiBase + url, options)
            } else {
                // If refresh failed, logout user
                await logout()
                throw new Error('Unauthorized: Token expired and refresh failed.')
            }
        }

        let data
        try {
            data = await res.json()
        } catch (e) {
            throw new Error('Response is not JSON')
        }

        if (!res.ok) {
            // API error, throw JSON error
            throw data
        }

        return data
    }

    return { fetchWithAuth }
}
