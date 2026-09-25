import { apiClient } from './api';

export interface EmployeeDirectoryItem {
  employee_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  department: string;
  job_title: string;
  employee_status: string;
  has_account: boolean;
  user_id?: number | null;
  username?: string | null;
  role_id?: number | null;
  role_name?: string | null;
  is_active?: boolean | null;
}

export interface ProvisionAccountPayload {
  employee_id: string;
  username: string;
  password: string;
  role_name: string;
}

export interface UserResponse {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  role_id: number;
  role_name: string;
  employee_id?: string | null;
  is_active: boolean;
  permissions: string[];
  created_at: string;
}

export interface RoleResponse {
  role_id: number;
  role_name: string;
  description?: string;
  permissions: string[];
}

export const adminApi = {
  getDirectory: async (): Promise<EmployeeDirectoryItem[]> => {
    const res = await apiClient.get<EmployeeDirectoryItem[]>('/admin/directory');
    return res.data;
  },

  provisionAccount: async (payload: ProvisionAccountPayload): Promise<UserResponse> => {
    const res = await apiClient.post<UserResponse>('/admin/provision', payload);
    return res.data;
  },

  updateRole: async (userId: number, roleName: string): Promise<UserResponse> => {
    const res = await apiClient.patch<UserResponse>(`/admin/users/${userId}/role`, {
      role_name: roleName,
    });
    return res.data;
  },

  toggleStatus: async (userId: number, isActive: boolean): Promise<UserResponse> => {
    const res = await apiClient.patch<UserResponse>(`/admin/users/${userId}/status`, {
      is_active: isActive,
    });
    return res.data;
  },

  getRoles: async (): Promise<RoleResponse[]> => {
    const res = await apiClient.get<RoleResponse[]>('/admin/roles');
    return res.data;
  },
};
