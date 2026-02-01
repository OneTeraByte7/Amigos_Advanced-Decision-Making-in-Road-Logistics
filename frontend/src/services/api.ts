import axios from 'axios'
import { FleetState, FleetMetrics, MatchingResult, RouteDecision } from '../types'

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
}

declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

// Use Vite environment variable when provided (set in Vercel or local .env)
const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || '/api'

export const api = {
  async initialize() {
    const response = await axios.post(`${BASE_URL}/initialize`, {})
    return response.data
  },

  async getState(): Promise<FleetState> {
    const response = await axios.get(`${BASE_URL}/state`)
    return response.data
  },

  async getMetrics(): Promise<FleetMetrics> {
    const response = await axios.get(`${BASE_URL}/metrics`)
    return response.data
  },

  async matchLoads(): Promise<MatchingResult> {
    const response = await axios.post(`${BASE_URL}/match-loads`)
    return response.data
  },

  async manageRoutes(): Promise<{ routes_managed: number; decisions: RouteDecision[] }> {
    const response = await axios.post(`${BASE_URL}/manage-routes`)
    return response.data
  },

  async runCycle() {
    const response = await axios.post(`${BASE_URL}/cycle`)
    return response.data
  },

  async getVehicles() {
    const response = await axios.get(`${BASE_URL}/vehicles`)
    return response.data
  },

  async getLoads() {
    const response = await axios.get(`${BASE_URL}/loads`)
    return response.data
  },

  async simulateMovement() {
    const response = await axios.post(`${BASE_URL}/simulate-movement`)
    return response.data
  }
}