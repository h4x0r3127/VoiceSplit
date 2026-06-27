import { api } from './api'
import type { TokenResponse } from '@/types/api'

const BASE = '/api/v1/auth'

export async function login(email: string, password: string): Promise<TokenResponse> {
  return api.post<TokenResponse>(`${BASE}/login`, { email, password })
}

export async function register(email: string, password: string, name: string): Promise<TokenResponse> {
  return api.post<TokenResponse>(`${BASE}/register`, { email, password, name })
}

export async function googleAuth(idToken: string): Promise<TokenResponse> {
  return api.post<TokenResponse>(`${BASE}/google`, { idToken })
}

export async function forgotPassword(email: string): Promise<void> {
  return api.post<void>(`${BASE}/forgot-password`, { email })
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  return api.post<void>(`${BASE}/reset-password`, { token, newPassword })
}
