import { useQuery } from '@tanstack/react-query';
import { fetchAllUsersApi } from '@/lib/api';
import { User } from '@/types/user';

export const useUserQuery = () => {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      try {
        return await fetchAllUsersApi();
      } catch (err) {
        console.warn('API failed, showing only mock data');
        return [];
      }
    },
  });
};
