export type Platform = 'gitlab' | 'mattermost' | 'drive';

export interface User {
  id: string;
  username: string;
  avatar?: string;
  email: string;
  createdAt: string;
  platforms: Partial<Record<Platform, PlatformConfig>>;
}

export type PlatformConfig = GitLabConfig | MattermostConfig | DriveConfig;

export interface GitLabConfig {
  role: 'Developer' | 'Maintainer';
  groupId: string;
  repoAccess: string[];
}

export interface MattermostConfig {
  serverUrl: string;
  teamName: string;
  defaultChannels: string[];
}

export interface DriveConfig {
  storageLimitMB: number;
  sharedFolderId: string;
  permissionLevel: 'reader' | 'writer' | 'commenter';
}
