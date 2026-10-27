export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "https://dogs.jonathancocuy-dev.online";

export const ENDPOINTS = {
  videoStream: `${API_URL}/video-stream`,
  latestReport: `${API_URL}/latest-report`,
  history: `${API_URL}/history`,
} as const;
