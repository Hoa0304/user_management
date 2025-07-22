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
import { Plus, Gitlab, Folder, MessageCircle, Database, Cloud, Slack } from 'lucide-react';
import { useState } from 'react';

export default function CreateUserModal() {
    const [open, setOpen] = useState(false);
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

    const iconMap: Record<string, React.ReactNode> = {
        gitlab: <Gitlab className="w-4 h-4" />,
        mattermost: <MessageCircle className="w-4 h-4" />,
        drive: <Folder className="w-4 h-4" />,
        slack: <Slack className="w-4 h-4" />,
        cloud: <Cloud className="w-4 h-4" />,
        database: <Database className="w-4 h-4" />,
    };

    const colorMap: Record<string, string> = {
        gitlab: '#FF6347',
        mattermost: '#0058cc',
        drive: '#0F9D58',
        slack: '#611f69',
        cloud: '#00c6ff',
        database: '#8e44ad',
    };

    const platforms = ['gitlab', 'mattermost', 'drive', 'slack', 'cloud', 'database'];

    const togglePlatform = (platform: string) => {
        setSelectedPlatforms((prev) =>
            prev.includes(platform)
                ? prev.filter((p) => p !== platform)
                : [...prev, platform]
        );
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
                    <DialogTitle>Create New User</DialogTitle>
                </DialogHeader>
                <form className="space-y-4 mt-2">
                    <div>
                        <label className="text-sm font-medium">Username</label>
                        <input
                            type="text"
                            placeholder="Enter username"
                            className="w-full mt-1 p-2 border rounded-md"
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium">Email</label>
                        <input
                            type="email"
                            placeholder="Enter email"
                            className="w-full mt-1 p-2 border rounded-md"
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium">Password</label>
                        <input
                            type="password"
                            placeholder="Enter password"
                            className="w-full mt-1 p-2 border rounded-md"
                        />
                    </div>

                    {/* Platform Access */}
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
                                        <div>
                                            <label className="block font-medium mb-1">Server URL</label>
                                            <input
                                                type="text"
                                                placeholder={`https://${platform}.company.com`}
                                                className="w-full border rounded-md p-2"
                                            />
                                        </div>
                                        <div>
                                            <label className="block font-medium mb-1">Access Level</label>
                                            <select className="w-full border rounded-md p-2">
                                                <option>Viewer</option>
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
                                            />
                                        </div>
                                        <div>
                                            <label className="block font-medium mb-1">Storage Limit</label>
                                            <input
                                                type="text"
                                                placeholder="e.g. 5GB"
                                                className="w-full border rounded-md p-2"
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                    <DialogFooter className="mt-4">
                        <Button type="submit" className="bg-[#0033FF] text-white">
                            Create User
                        </Button>
                        <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                            Cancel
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>

    );
}
