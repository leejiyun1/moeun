export const tokenStorage = {
  getAccessToken: () => localStorage.getItem('access_token'),
  setAccessToken: (value: string) =>
    localStorage.setItem('access_token', value),
  removeAccessToken: () => localStorage.removeItem('access_token'),

  getRefreshToken: () => localStorage.getItem('refresh_token'),
  setRefreshToken: (value: string) =>
    localStorage.setItem('refresh_token', value),
  removeRefreshToken: () => localStorage.removeItem('refresh_token'),
}
