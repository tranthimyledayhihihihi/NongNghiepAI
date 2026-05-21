const SOURCE_META = {
  official: {
    label: 'Nguồn chính thức Bộ Nông nghiệp Việt Nam',
    shortLabel: 'Chính thức',
    tone: 'official',
  },
  realtime: {
    label: 'Open-Meteo realtime',
    shortLabel: 'Realtime',
    tone: 'realtime',
  },
  cache: {
    label: 'Dữ liệu DB',
    shortLabel: 'DB',
    tone: 'cache',
  },
  retail: {
    label: 'Giá tham chiếu bán lẻ',
    shortLabel: 'Bán lẻ',
    tone: 'retail',
  },
  ai: {
    label: 'AI phân tích',
    shortLabel: 'AI',
    tone: 'ai',
  },
  weatherRule: {
    label: 'AI phân tích',
    shortLabel: 'AI',
    tone: 'ai',
  },
  openMeteo: {
    label: 'Open-Meteo',
    shortLabel: 'Open-Meteo',
    tone: 'weather',
  },
};

const SOURCE_ALIASES = {
  official: 'official',
  realtime: 'realtime',
  realtime_api: 'realtime',
  cache: 'cache',
  cached: 'cache',
  database: 'cache',
  db: 'cache',
  retail: 'retail',
  ai: 'ai',
  ai_generated: 'ai',
  rule_based_ai: 'ai',
  weather_rule_ai: 'weatherRule',
  open_meteo_rule: 'weatherRule',
  openmeteo: 'openMeteo',
  'open-meteo': 'openMeteo',
};

const TONE_CLASS_MAP = {
  official: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  realtime: 'border-sky-200 bg-sky-50 text-sky-700',
  cache: 'border-slate-200 bg-slate-100 text-slate-700',
  retail: 'border-amber-200 bg-amber-50 text-amber-700',
  ai: 'border-violet-200 bg-violet-50 text-violet-700',
  weather: 'border-cyan-200 bg-cyan-50 text-cyan-700',
  default: 'border-slate-200 bg-slate-50 text-slate-700',
};

const TONE_ICON_CLASS_MAP = {
  official: 'text-emerald-600',
  realtime: 'text-sky-600',
  cache: 'text-slate-600',
  retail: 'text-amber-600',
  ai: 'text-violet-600',
  weather: 'text-cyan-600',
  default: 'text-slate-500',
};

export function resolveSourceKey(source) {
  if (!source) {
    return '';
  }

  if (typeof source === 'string') {
    const normalized = source.trim().toLowerCase();
    return SOURCE_ALIASES[normalized] || normalized;
  }

  if (typeof source === 'object') {
    const candidate =
      source.sourceType ||
      source.type ||
      source.kind ||
      source.source ||
      source.provider ||
      source.source_name ||
      source.sourceName ||
      source.provider_label ||
      source.name ||
      source.label;

    return resolveSourceKey(candidate);
  }

  return '';
}

export function getSourceMeta(source) {
  const key = resolveSourceKey(source);

  if (!key) {
    return {
      key: '',
      label: '',
      shortLabel: '',
      tone: 'default',
      badgeClassName: TONE_CLASS_MAP.default,
      iconClassName: TONE_ICON_CLASS_MAP.default,
    };
  }

  const meta = SOURCE_META[key];

  if (meta) {
    return {
      key,
      ...meta,
      badgeClassName: TONE_CLASS_MAP[meta.tone] || TONE_CLASS_MAP.default,
      iconClassName: TONE_ICON_CLASS_MAP[meta.tone] || TONE_ICON_CLASS_MAP.default,
    };
  }

  return {
    key,
    label: source?.label || source?.name || source?.provider_label || source?.source_name || source?.sourceName || source?.sourceType || key,
    shortLabel: source?.shortLabel || source?.label || source?.provider_label || source?.source_name || key,
    tone: 'default',
    badgeClassName: TONE_CLASS_MAP.default,
    iconClassName: TONE_ICON_CLASS_MAP.default,
  };
}

export function getSourceLabel(source) {
  return getSourceMeta(source).label;
}

export function getSourceShortLabel(source) {
  return getSourceMeta(source).shortLabel;
}

export function getSourceTone(source) {
  return getSourceMeta(source).tone;
}

export function getSourceBadgeClassName(source) {
  return getSourceMeta(source).badgeClassName;
}

export function getSourceIconClassName(source) {
  return getSourceMeta(source).iconClassName;
}

export { SOURCE_META, TONE_CLASS_MAP, TONE_ICON_CLASS_MAP };
export default SOURCE_META;
