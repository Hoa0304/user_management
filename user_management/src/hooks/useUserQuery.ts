import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { User } from '@/types/user';

const mockUsers: User[] = [
  {
    id: '1',
    username: 'johndoe',
    avatar: 'https://phanmemmkt.vn/wp-content/uploads/2024/09/avt-Facebook-hai-huoc-2.jpg',
    email: 'johndoe@example.com',
    created_at: '2025-07-22T10:00:00Z',
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
    created_at: '2025-07-21T09:30:00Z',
    platforms: {
      drive: {
        storageLimitMB: 1000,
        sharedFolderId: 'folder-456',
        permissionLevel: 'writer',
      },
    },
  },
  {
    id: '3',
    username: 'baeeee',
    email: 'baeeeee@gmail.com',
    avatar: 'https://img.hoidap247.com/picture/question/20200508/large_1588936738888.jpg',
    created_at: '2025-07-28T09:30:00Z',
    platforms: {
      mattermost: {
        serverUrl: 'https://chat.example.com',
        teamName: 'engineering',
        defaultChannels: ['general', 'dev'],
      },
      drive: {
        storageLimitMB: 1000,
        sharedFolderId: 'folder-456',
        permissionLevel: 'writer',
      },
      gitlab: {
        role: 'Maintainer',
        groupId: '123',
        repoAccess: ['repo1', 'repo2'],
      },
    },
  },
];

export const useUserQuery = () => {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      try {
        const res = await axios.get<User[]>('http://localhost:8000/api/all_users');
        return [...res.data, ...mockUsers];
      } catch (err) {
        console.warn('API failed, showing only mock data');
        return mockUsers;
      }
    },
  });
};
