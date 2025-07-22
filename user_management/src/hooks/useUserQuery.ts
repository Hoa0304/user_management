import { useQuery } from '@tanstack/react-query';
import { User } from '@/types/user';

const mockUsers: User[] = [
  {
    id: '1',
    username: 'johndoe',
    avatar: 'https://phanmemmkt.vn/wp-content/uploads/2024/09/avt-Facebook-hai-huoc-2.jpg',
    email: 'johndoe@example.com',
    createdAt: '2025-07-22T10:00:00Z',
    platforms: {
      gitlab: {
        role: 'Developer',
        groupId: 'group-123',
        repoAccess: ['repo1', 'repo2'],
      },
      mattermost: {
        serverUrl: 'https://chat.example.com',
        teamName: 'engineering',
        defaultChannels: ['general', 'dev'],
      },
    },
  },
  {
    id: '2',
    username: 'janedoe',
    email: 'janedoe@example.com',
    createdAt: '2025-07-21T09:30:00Z',
    platforms: {
      drive: {
        storageLimitMB: 1000,
        sharedFolderId: 'folder-456',
        permissionLevel: 'writer',
      },
    },
  },
];

export const useUserQuery = () => {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      // Simulate delay like a real API
      await new Promise((res) => setTimeout(res, 500));
      return mockUsers;
    },
  });
};
