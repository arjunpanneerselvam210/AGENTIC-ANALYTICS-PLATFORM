export interface UserRole {
  role_id: number;
  role_name: string;
  description?: string;
}

export interface UserProfile {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  name?: string;
  employee_id?: string | null;
  role: string;
  permissions: string[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    user_id: number;
    username: string;
    email: string;
    full_name: string;
    employee_id?: string | null;
    role: string;
  };
}
