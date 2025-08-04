export const normalizeConfigs = (configs: Record<string, any>) => {
    const normalized: Record<string, any> = {};
    for (const platform in configs) {
        const config = configs[platform];
        switch (platform) {
            case 'gitlab':
                normalized[platform] = {
                    platform,
                    role: config.role,
                    group_id: config.group_id,
                    repo_access: config.repo_access,
                };
                break;
            case 'mattermost':
                normalized[platform] = {
                    platform,
                    server_name: config.server_name,
                    team: config.team,
                    default_channels: config.default_channels,
                    role: config.role,
                };
                break;
            case 'drive':
                normalized[platform] = {
                    platform,
                    storage_limit: config.storage_limit,
                    shared_folder_id: config.shared_folder_id,
                    permission: config.permission,
                };
                break;
            case 'nextcloud':
                normalized[platform] = {
                    platform,
                    role: config.role,
                    group_id: config.group_id,
                    storage_limit: config.storage_limit,
                    shared_folder_id: config.shared_folder_id,
                    permission: config.permission,
                };
                break;
            default:
                normalized[platform] = {
                    ...config,
                    platform,
                };
        }
    }
    return normalized;
};