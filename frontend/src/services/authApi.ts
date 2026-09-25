import { apiClient } from './api';
import type { LoginResponse, UserProfile } from '../types/auth';

export const authApi = {
  /**
   * Authenticate application user and retrieve JWT token.
   * Uses URL-encoded form data as expected by OAuth2PasswordRequestForm in FastAPI.
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Retrieve current authenticated user's profile and granted permissions.
   */
  async getMe(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/auth/me');
    return response.data;
  }
};
