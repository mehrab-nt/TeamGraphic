import { useAuth } from './useAuth'

export function useApi() {
    const { getAccessToken, tryRefreshToken } = useAuth()

    async function fetchWithAuth(url, options = {}) {
        let token = getAccessToken()
        if (!options.headers) options.headers = {}
        options.headers.Authorization = `Bearer ${token}`

        let res = await fetch(process.env.PUBLIC_API_BASE + url, options)
        if (res.status === 401) {
            // Try refresh token once
            if (tryRefreshToken) {
                const refreshed = await tryRefreshToken()
                if (refreshed) {
                    token = getAccessToken()
                    options.headers.Authorization = `Bearer ${token}`
                    res = await fetch(process.env.PUBLIC_API_BASE + url, options)
                } else {
                    throw new Error('Unauthorized and refresh failed')
                }
            } else {
                throw new Error('Unauthorized and no refresh function')
            }
        }
        if (!res.ok) {
            const error = await res.json()
            throw error
        }
        return await res.json()
    }

    return { fetchWithAuth }
}
