import { AlertTriangle, BadgeCheck, Database, RefreshCw, Sparkles } from 'lucide-react';
import { getSourceBadgeProps } from '../utils/sourceMeta';

const BADGE_STYLES = {
  realtime_api: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  database: 'border-slate-200 bg-slate-50 text-slate-800',
  cached: 'border-blue-200 bg-blue-50 text-blue-800',
  ai_generated: 'border-violet-200 bg-violet-50 text-violet-800',
  mock: 'border-amber-200 bg-amber-50 text-amber-800',
  legacy: 'border-gray-200 bg-gray-100 text-gray-700',
};

const ICONS = {
  realtime_api: RefreshCw,
  database: Database,
  cached: BadgeCheck,
  ai_generated: Sparkles,
  mock: AlertTriangle,
  legacy: Database,
};

const DataSourceBadge = ({ data = {}, compact = false, defaultSource = 'database' }) => {
  const { key, label, meta } = getSourceBadgeProps(data, defaultSource);
  const Icon = ICONS[meta.source] || Database;
  const className = [
    'inline-flex items-center gap-1 rounded-full border font-semibold',
    compact ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs',
    BADGE_STYLES[meta.source] || BADGE_STYLES.database,
  ].join(' ');

  return (
    <span className={className} data-source-key={key} title={meta.source_name || label}>
      <Icon className={compact ? 'h-3 w-3' : 'h-3.5 w-3.5'} />
      <span>{label}</span>
    </span>
  );
};

export default DataSourceBadge;
