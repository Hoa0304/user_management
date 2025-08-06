'use client';

import {
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
    Plus,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';
import { UserModalProps } from '@/types/user';
import { colorMap, iconMap, platforms } from '@/lib/constants';
import { denormalizeConfigs, normalizeConfigs } from '@/lib/normalizeConfigs';

export default function UserModal({ mode, open, setOpen, defaultValues, onSuccess }: UserModalProps) {
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
    });
    const [platformConfigs, setPlatformConfigs] = useState<Record<string, any>>({});

    useEffect(() => {
        if (defaultValues) {
            setFormData({
                username: defaultValues.username || '',
                email: defaultValues.email || '',
                password: (defaultValues as any).password || '',
            });

            const normalized = denormalizeConfigs(defaultValues.platforms || []);
            setSelectedPlatforms(Object.keys(normalized));
            setPlatformConfigs(normalized);
        }
    }, [defaultValues])

    const togglePlatform = (platform: string) => {
        setSelectedPlatforms((prev) => {
            const isSelected = prev.includes(platform);
            const updated = isSelected
                ? prev.filter((p) => p !== platform)
                : [...prev, platform];

            if (!isSelected) {
                setPlatformConfigs((prevConfigs) => ({
                    ...prevConfigs,
                    [platform]: {
                        ...(platform === 'gitlab' && { role: 'Guest', group_id: '', repo_access: [] }),
                        ...(platform === 'mattermost' && {
                            server_name: '',
                            team: '',
                            default_channels: [],
                            role: 'team_member',
                        }),
                        ...(platform === 'nextcloud' && {
                            storage_limit: '',
                            shared_folder_id: '',
                            permission: 'viewer',
                        }),
                        ...(platform === 'drive' && {
                            shared_folder_id: '',
                            permission: 'viewer',
                        }),
                    },
                }));
            }

            return updated;
        });
    };


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const payload = {
            ...formData,
            ...(formData.password !== '' && { password: formData.password }),
            platforms: normalizeConfigs(platformConfigs),
        };

        try {
            if (mode === 'create') {
                await axios.post('http://localhost:8000/api/users', payload);
            } else if (mode === 'edit' && defaultValues?.username) {
                await axios.patch(`http://localhost:8000/api/users/${defaultValues.username}`, payload);
            }
            onSuccess?.();
            setOpen(false);
        } catch (err) {
            const error = err as AxiosError<{ detail?: string }>;
            console.error('Error:', error.response?.data || error.message);
            alert(`Error: ${error.response?.data?.detail || error.message}`);
        }

    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-[#0033FF]">
                    <Plus className="mr-2 h-4 w-4" /> Add User
                </Button>
            </DialogTrigger>
            <DialogContent className="w-full">
                <DialogHeader>
                    <DialogTitle>{mode === 'create' ? 'Create New User' : 'Edit User'}</DialogTitle>
                </DialogHeader>
                <div className="overflow-y-auto max-h-[75vh] mt-2 scroll-hidden">
                    <form onSubmit={handleSubmit} className="space-y-4 mt-2">
                        {['username', 'email', 'password'].map((field) => (
                            <div key={field}>
                                <label className="text-sm font-medium capitalize">{field}</label>
                                <input
                                    type={field === 'password' ? 'password' : 'text'}
                                    placeholder={`Enter ${field}`}
                                    className="w-full mt-1 p-2 border rounded-md"
                                    value={(formData as any)[field]}
                                    onChange={(e) =>
                                        setFormData({ ...formData, [field]: e.target.value })
                                    }
                                    required={field !== 'password' || mode === 'create'}
                                />
                            </div>
                        ))}



                        {/* Platforms */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {platforms.map((platform) => (
                                <div key={platform} className="border px-4 py-3 rounded-md space-y-3">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="w-6 h-6 rounded-md flex items-center justify-center text-white"
                                                style={{ backgroundColor: colorMap[platform] || '#999' }}
                                            >
                                                {iconMap[platform] || '?'}
                                            </div>
                                            <span className="capitalize">{platform}</span>
                                        </div>
                                        <label className="relative inline-flex items-center cursor-pointer">
                                            <input
                                                type="checkbox"
                                                className="sr-only peer"
                                                checked={selectedPlatforms.includes(platform)}
                                                onChange={() => togglePlatform(platform)}
                                            />
                                            <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-all duration-200"></div>
                                            <span className="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full transition-all duration-200 peer-checked:translate-x-full"></span>
                                        </label>
                                    </div>

                                    {selectedPlatforms.includes(platform) && (
                                        <div className="grid gap-3 text-sm text-gray-800">
                                            {platform === 'gitlab' && (
                                                <>
                                                    <div>
                                                        <label className="block font-medium mb-1">Role</label>
                                                        <select
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.role || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        role: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        >
                                                            <option>Guest</option>
                                                            <option>Reporter</option>
                                                            <option>Developer</option>
                                                            <option>Maintainer</option>
                                                            <option>Owner</option>
                                                        </select>
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Group ID</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. 123"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.group_id || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        group_id: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Repo Access</label>
                                                        <input
                                                            type="text"
                                                            placeholder="repo1,repo2"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.repo_access}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        repo_access: e.target.value.split(',').map((r) => r.trim()),
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                </>
                                            )}

                                            {platform === 'mattermost' && (
                                                <>
                                                    <div>
                                                        <label className="block font-medium mb-1">Server Name</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. chat.company.com"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.server_name || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        server_name: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Team</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. dev-team"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.team || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        team: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Role</label>
                                                        <select
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.role}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        role: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                            required
                                                        >
                                                            <option value="team_member">Member</option>
                                                            <option value="team_admin">Admin</option>
                                                        </select>

                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Default Channels</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. general,dev"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.default_channels || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        default_channels: e.target.value.split(',').map((c) => c.trim()),
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                </>
                                            )}

                                            {platform === 'drive' && (
                                                <>
                                                    {/* <div>
                                                        <label className="block font-medium mb-1">Storage Limit (MB)</label>
                                                        <input
                                                            type="number"
                                                            placeholder="e.g. 5000"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.storage_limit || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        storage_limit: parseInt(e.target.value),
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div> */}
                                                    <div>
                                                        <label className="block font-medium mb-1">Shared Folder</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. 1D_c5qz8XN..."
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.shared_folder_id || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        shared_folder_id: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Permission Level</label>
                                                        <select
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.permission || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        permission: e.target.value.toLowerCase(),
                                                                    },
                                                                }))
                                                            }
                                                        >
                                                            <option>Viewer</option>
                                                            <option>Commenter</option>
                                                            <option>Writer</option>
                                                            <option>Organizer</option>
                                                        </select>
                                                    </div>
                                                </>
                                            )}
                                            {platform === 'nextcloud' && (
                                                <>
                                                    <div>
                                                        <label className="block font-medium mb-1">Group ID</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. 123"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.group_id || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        group_id: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Storage Limit (MB)</label>
                                                        <input
                                                            type="number"
                                                            placeholder="e.g. 5000"
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.storage_limit || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        storage_limit: parseFloat(e.target.value),
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Shared Folder</label>
                                                        <input
                                                            type="text"
                                                            placeholder="e.g. 1D_c5qz8XN..."
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.shared_folder_id || ''}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        shared_folder_id: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block font-medium mb-1">Permission Level</label>
                                                        <select
                                                            className="w-full border rounded-md p-2"
                                                            value={platformConfigs[platform]?.permission}
                                                            onChange={(e) =>
                                                                setPlatformConfigs((prev) => ({
                                                                    ...prev,
                                                                    [platform]: {
                                                                        ...prev[platform],
                                                                        permission: e.target.value,
                                                                    },
                                                                }))
                                                            }
                                                        >
                                                            <option value="Viewer">Viewer</option>
                                                            <option value="Editor">Editor</option>
                                                        </select>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                        <DialogFooter className="mt-4">
                            <Button type="submit" className="bg-[#0033FF] text-white">
                                {mode === 'create' ? 'Create User' : 'Update User'}
                            </Button>
                            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                                Cancel
                            </Button>
                        </DialogFooter>
                    </form>
                </div>
            </DialogContent>
        </Dialog>
    );
}
