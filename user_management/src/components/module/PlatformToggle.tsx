import { colorMap, iconMap } from '@/lib/constants';
import { ReactNode } from 'react';

interface Props {
  platform: string;
  selectedPlatforms: string[];
  togglePlatform: (platform: string) => void;
  children?: ReactNode;
}

export default function PlatformToggle({ platform, selectedPlatforms, togglePlatform, children }: Props) {
  return (
    <div className="border px-4 py-3 rounded-md space-y-3">
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
      {children}
    </div>
  );
}
