export type Platform = 'gitlab' | 'mattermost' | 'drive' |'nextcloud';

export interface User {
  id: string;
  username: string;
  avatar?: string;
  email: string;
  created_at: string;
  platforms: Partial<Record<Platform, PlatformConfig>>;
}

export type PlatformConfig = GitLabConfig | MattermostConfig | NextCloudConfig |DriveConfig;

export interface GitLabConfig {
  role: 'Developer' | 'Maintainer' | "Owner" | "Guest" | "Reporter";
  group_id: string;
  repoAccess: string[];
}

export interface MattermostConfig {
  server_name: string;
  team: string;
  role: '' |'Member' | 'Admin';
  default_channels: string[];
}

export interface DriveConfig {
  storageLimitMB: number;
  sharedFolderId: string;
  permissionLevel: 'reader' | 'writer' | 'commenter';
}

export interface NextCloudConfig {
  group_id: string;
  storageLimitMB: number;
  sharedFolderId: string;
  permission: ''|'viewer' | 'editor';
}

export type UserModalProps = {
  mode: 'create' | 'edit';
  open: boolean;
  setOpen: (val: boolean) => void;
  defaultValues?: {
    id?: string;
    username: string;
    email: string;
    password?: string;
    platforms: Record<string, any>;
  };
  onSuccess?: () => void;
};
