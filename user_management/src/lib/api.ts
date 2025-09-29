import axios from 'axios';
import { User } from '@/types/user';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const deleteUserApi = async (username: string) => {
  return await api.delete(`/api/users/${username}`);
};

export const revokeDriveAccessApi = async (folder_id: string, permission_id: string) => {
  return await api.delete(`/google-drive/revoke-access`, {
    data: { folder_id, permission_id },
  });
};

export const fetchAllUsersApi = async (): Promise<User[]> => {
  const res = await api.get<User[]>(`/api/all_users`);
  return res.data;
};

export const createUserApi = async (payload: any) => {
  return await api.post(`/api/users`, payload);
};

export const editUserApi = async (username: string, payload: any) => {
  return await api.patch(`/api/users/${username}`, payload);
};
