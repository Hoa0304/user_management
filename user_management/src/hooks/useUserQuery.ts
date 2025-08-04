import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { User } from '@/types/user';

export const useUserQuery = () => {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      try {
<<<<<<< Updated upstream
        const res = await axios.get<User[]>('http://localhost:8000/gitlab/users');
        return [...res.data, ...mockUsers];
=======
        const res = await axios.get<User[]>('http://localhost:8000/api/all_users');
        return [...res.data];
>>>>>>> Stashed changes
      } catch (err) {
        console.warn('API failed, showing only mock data');
        return [];
      }
    },
  });
};
