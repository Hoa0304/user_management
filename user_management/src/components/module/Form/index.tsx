'use client';

import {
    Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserModalProps } from '@/types/user';
import { platforms } from '@/lib/constants';
import { denormalizeConfigs, normalizeConfigs } from '@/lib/normalizeConfigs';
import PlatformToggle from '../PlatformToggle';
import PlatformConfigFields from '../PlatformConfigFields';

export default function UserModal({ mode, open, setOpen, defaultValues, onSuccess }: UserModalProps) {
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });
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
    }, [defaultValues]);

    const togglePlatform = (platform: string) => {
        setSelectedPlatforms((prev) => {
            const isSelected = prev.includes(platform);

            if (isSelected) {
                // If off → delete config
                setPlatformConfigs((prevConfigs) => {
                    const { [platform]: _, ...rest } = prevConfigs;
                    return rest;
                });
                return prev.filter((p) => p !== platform);
            } else {
                // If enable → add default config if not available
                setPlatformConfigs((prevConfigs) => ({
                    ...prevConfigs,
                    [platform]: prevConfigs[platform] || 
                    PlatformConfigFields.getDefaultConfig(platform, formData.email),
                }));
                return [...prev, platform];
            }
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const payload = {
            ...formData,
            ...(formData.password !== '' && { password: formData.password }),
            platforms: normalizeConfigs(platformConfigs, formData.email),
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
            console.error(err);
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
                                    onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
                                    required={field !== 'password' || mode === 'create'}
                                />
                            </div>
                        ))}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {platforms.map((platform) => (
                                <PlatformToggle
                                    key={platform}
                                    platform={platform}
                                    selectedPlatforms={selectedPlatforms}
                                    togglePlatform={togglePlatform}
                                >
                                    {selectedPlatforms.includes(platform) && (
                                        <PlatformConfigFields
                                            platform={platform}
                                            config={platformConfigs[platform] || {}}
                                            setConfig={(newConfig) =>
                                                setPlatformConfigs((prev) => ({
                                                    ...prev,
                                                    [platform]: { ...prev[platform], ...newConfig },
                                                }))
                                            }
                                        />
                                    )}
                                </PlatformToggle>
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
