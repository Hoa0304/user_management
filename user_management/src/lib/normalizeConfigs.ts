import { PlatformConfig } from "@/types/user";

export const normalizeConfigs = (configs: Record<string, any>) => {
    const normalized: any[] = [];

    for (const platform in configs) {
        const config = configs[platform];
        const base = { platform };

        if (!config) continue;

        if (platform === 'gitlab') {
            normalized.push({
                ...base,
                role: config.role,
                group_id: config.group_id,
                repo_access: (config.repo_access || []).map(Number),
            });
        } else if (platform === 'mattermost') {
            normalized.push({
                ...base,
                server_name: config.server_name,
                team: config.team,
                default_channels: config.default_channels,
                role: config.role,
            });
        } else if (platform === 'drive') {
            normalized.push({
                ...base,
                storage_limit: config.storage_limit,
                shared_folder_id: config.shared_folder_id,
                permission: config.permission,
            });
        } else if (platform === 'nextcloud') {
            normalized.push({
                ...base,
                role: config.role,
                group_id: config.group_id,
                storage_limit: config.storage_limit,
                shared_folder_id: config.shared_folder_id,
                permission: config.permission,
            });
        } else {
            normalized.push({ ...config, platform });
        }
    }

    return normalized;
};

export function denormalizeConfigs(configList: any[]): Record<string, any> {
  const result: Record<string, any> = {};
  for (const config of configList) {
    if (config.platform) {
      result[config.platform] = { ...config };
      delete result[config.platform].platform;
    }
  }
  return result;
}
