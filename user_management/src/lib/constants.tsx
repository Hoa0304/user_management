import { Icon } from '@iconify/react';
import nextcloudIcon from '@iconify-icons/simple-icons/nextcloud';
import mattermostIcon from '@iconify-icons/simple-icons/mattermost';
import {
  Gitlab,
  Folder,
  Database,
  Cloud,
  Slack,
} from 'lucide-react';

export const iconMap: Record<string, React.ReactNode> = {
  gitlab: <Gitlab className="w-4 h-4" />,
  mattermost: <Icon icon={mattermostIcon} width={16} height={16} />,
  drive: <Folder className="w-4 h-4" />,
  nextcloud: <Icon icon={nextcloudIcon} width={16} height={16} />,
  slack: <Slack className="w-4 h-4" />,
  cloud: <Cloud className="w-4 h-4" />,
  database: <Database className="w-4 h-4" />,
};

export const colorMap: Record<string, string> = {
  gitlab: '#FF6347',
  mattermost: '#0058cc',
  drive: '#0F9D58',
  nextcloud: '#0082c9',
  slack: '#611f69',
  cloud: '#00c6ff',
  database: '#8e44ad',
};

export const platforms = ['gitlab', 'mattermost', 'drive', 'nextcloud'];
