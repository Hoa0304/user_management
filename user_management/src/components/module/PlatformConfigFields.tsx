interface Props {
  platform: string;
  config: any;
  setConfig: (newConfig: any) => void;
}

export default function PlatformConfigFields({ platform, config, setConfig }: Props) {
  const updateField = (field: string, value: any) => {
    setConfig({
      ...config,
      [field]: value,
    });
  };

  if (platform === 'gitlab') {
    return (
      <div className="grid gap-3 text-sm text-gray-800">
        {/* Group ID */}
        <div>
          <label className="block font-medium mb-1">Group ID</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            placeholder="devs"
            value={config.group_id || ''}
            onChange={(e) => updateField('group_id', e.target.value)}
          />
        </div>
        {/* Role */}
        <div>
          <label className="block font-medium mb-1">Role</label>
          <select
            className="w-full border rounded-md p-2"
            value={config.role || ''}
            onChange={(e) => updateField('role', e.target.value)}
          >
            <option>Guest</option>
            <option>Reporter</option>
            <option>Developer</option>
            <option>Maintainer</option>
            <option>Owner</option>
          </select>
        </div>
        {/* Repo Access */}
        <div>
          <label className="block font-medium mb-1">Repo Access</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            placeholder="1,2"
            value={(config.repo_access || []).join(', ')}
            onChange={(e) =>
              updateField(
                'repo_access',
                e.target.value.split(',').map((r) => r.trim())
              )
            }
          />
        </div>
      </div>
    );
  }

  if (platform === 'mattermost') {
    return (
      <div className="grid gap-3 text-sm text-gray-800">
        {/* Server Name */}
        <div>
          <label className="block font-medium mb-1">Server Name</label>
          <input
            type="text"
            placeholder="ikya.dev.com"
            className="w-full border rounded-md p-2"
            value={config.server_name || ''}
            onChange={(e) => updateField('server_name', e.target.value)}
          />
        </div>
        {/* Team */}
        <div>
          <label className="block font-medium mb-1">Team</label>
          <input
            type="text"
            placeholder="ikya"
            className="w-full border rounded-md p-2"
            value={config.team || ''}
            onChange={(e) => updateField('team', e.target.value)}
          />
        </div>
        {/* Default Channels */}
        <div>
          <label className="block font-medium mb-1">Default Channels</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            placeholder="Town Square, Off-Topic"
            value={(config.default_channels || []).join(', ')}
            onChange={(e) =>
              updateField(
                'default_channels',
                e.target.value.split(',').map((c) => c.trim())
              )
            }
          />
        </div>
        {/* Role */}
        <div>
          <label className="block font-medium mb-1">Role</label>
          <select
            className="w-full border rounded-md p-2"
            value={config.role || 'Member'}
            onChange={(e) => updateField('role', e.target.value)}
          >
            <option>Member</option>
            <option>Admin</option>
          </select>
        </div>
      </div>
    );
  }

  if (platform === 'nextcloud') {
    return (
      <div className="grid gap-3 text-sm text-gray-800">
        {/* Storage Limit */}
        <div>
          <label className="block font-medium mb-1">Storage Limit (MB)</label>
          <input
            type="number"
            className="w-full border rounded-md p-2"
            placeholder="512"
            value={config.storage_limit || ''}
            onChange={(e) => updateField('storage_limit', e.target.value)}
          />
        </div>
        {/* Shared Folder ID */}
        <div>
          <label className="block font-medium mb-1">Shared Folder ID</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            placeholder="/documents"
            value={config.shared_folder_id || ''}
            onChange={(e) => updateField('shared_folder_id', e.target.value)}
          />
        </div>
        {/* Permission */}
        <div>
          <label className="block font-medium mb-1">Permission</label>
          <select
            className="w-full border rounded-md p-2"
            value={config.permission || 'viewer'}
            onChange={(e) => updateField('permission', e.target.value)}
          >
            <option value="viewer">Viewer</option>
            <option value="editor">Editor</option>
          </select>
        </div>
      </div>
    );
  }

  if (platform === 'drive') {
    return (
      <div className="grid gap-3 text-sm text-gray-800">
        {/* Shared Folder ID */}
        <div>
          <label className="block font-medium mb-1">Shared Folder ID</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            placeholder="1D_c5qz8XNspoGn1o5Ps5NfWU72OSFYES"
            value={config.shared_folder_id || ''}
            onChange={(e) => updateField('shared_folder_id', e.target.value)}
          />
        </div>
        {/* Role */}
        <div>
          <label className="block font-medium mb-1">Role</label>
          <select
            className="w-full border rounded-md p-2"
            value={config.role || 'reader'}
            onChange={(e) => updateField('role', e.target.value)}
          >
            <option value="reader">Reader</option>
            <option value="writer">Writer</option>
            <option value="commenter">Commenter</option>
          </select>
        </div>
        {/* User Email */}
        <div>
          <label className="block font-medium mb-1">User Email</label>
          <input
            type="email"
            className="w-full border rounded-md p-2"
            value={config.user_email || ''}
            onChange={(e) => updateField('user_email', e.target.value)}
            readOnly
          />
        </div>
        {/* Permission ID */}
        <div>
          <label className="block font-medium mb-1">Permission ID</label>
          <input
            type="text"
            className="w-full border rounded-md p-2"
            value={config.permission_id || ''}
            onChange={(e) => updateField('permission_id', e.target.value)}
            readOnly
          />
        </div>
      </div>
    );
  }

  return null;
}

PlatformConfigFields.getDefaultConfig = (platform: string, email: string) => {
  switch (platform) {
    case 'gitlab':
      return { role: 'Guest', group_id: '', repo_access: [] };
    case 'mattermost':
      return { server_name: '', team: '', default_channels: [], role: 'Member' };
    case 'nextcloud':
      return { storage_limit: '', shared_folder_id: '', permission: 'viewer' };
    case 'drive':
      return { shared_folder_id: '', role: 'reader', user_email: email, permission_id: '' };
    default:
      return {};
  }
};
