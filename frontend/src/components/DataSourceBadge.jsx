import React from 'react';
import {
  BadgeCheck,
  Bot,
  CloudSun,
  Database,
  RefreshCw,
  ShoppingBag,
  Zap,
} from 'lucide-react';
import {
  getSourceBadgeClassName,
  getSourceIconClassName,
  getSourceMeta,
} from '../utils/sourceMeta';

const ICON_MAP = {
  official: BadgeCheck,
  realtime: Zap,
  cache: Database,
  retail: ShoppingBag,
  ai: Bot,
  weather: CloudSun,
  default: RefreshCw,
};

export function DataSourceBadge({
  source,
  type,
  variant,
  label,
  className = '',
  compact = false,
  showLabel = true,
  title,
}) {
  const meta = getSourceMeta(source || type || variant || label);
  const Icon = ICON_MAP[meta.tone] || ICON_MAP.default;
  const resolvedLabel = label || meta.label || meta.shortLabel || '';
  const resolvedTitle = title || resolvedLabel;

  if (!resolvedLabel && !compact) {
    return null;
  }

  return (
    <span
      className={[
        'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium leading-5',
        getSourceBadgeClassName(source || type || variant || label),
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      title={resolvedTitle}
    >
      <Icon
        className={[
          'h-3.5 w-3.5',
          getSourceIconClassName(source || type || variant || label),
        ]
          .filter(Boolean)
          .join(' ')}
      />
      {showLabel ? <span>{compact ? meta.shortLabel || resolvedLabel : resolvedLabel}</span> : null}
    </span>
  );
}

export default DataSourceBadge;
