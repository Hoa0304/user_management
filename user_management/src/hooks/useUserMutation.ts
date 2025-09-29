import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createUserApi, editUserApi } from '@/lib/api';

export const useUserMutation = (mode: 'create' | 'edit', username?: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: any) => {
      if (mode === 'create') {
        return await createUserApi(payload);
      } else if (mode === 'edit' && username) {
        return await editUserApi(username, payload);
      }
      throw new Error('Invalid mode or missing username');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
