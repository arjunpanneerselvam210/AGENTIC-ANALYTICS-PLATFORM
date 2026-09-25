/**
 * Indian Standard Time (IST, UTC+05:30) Time Utilities.
 * Formats all application timestamps, live telemetry, and chat clocks in IST.
 */

const IST_TIMEZONE = 'Asia/Kolkata';

/**
 * Formats a date/timestamp into IST time string: "10:35 PM" or "10:35:12 PM"
 */
export const formatISTTime = (
  date?: string | Date | number | null,
  includeSeconds: boolean = false
): string => {
  if (!date) return 'Live';
  try {
    const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
    if (isNaN(d.getTime())) return 'Live';
    return d.toLocaleTimeString('en-IN', {
      timeZone: IST_TIMEZONE,
      hour: '2-digit',
      minute: '2-digit',
      ...(includeSeconds ? { second: '2-digit' } : {}),
      hour12: true,
    });
  } catch {
    return 'Live';
  }
};

/**
 * Formats a date/timestamp into IST date string: "25 Sep 2026"
 */
export const formatISTDate = (
  date?: string | Date | number | null
): string => {
  if (!date) return '';
  try {
    const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-IN', {
      timeZone: IST_TIMEZONE,
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return '';
  }
};

/**
 * Formats into full IST DateTime string: "25 Sep 2026, 10:35 PM IST"
 */
export const formatISTDateTime = (
  date?: string | Date | number | null,
  includeSeconds: boolean = false
): string => {
  if (!date) return '';
  try {
    const d = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
    if (isNaN(d.getTime())) return '';
    const formatted = d.toLocaleString('en-IN', {
      timeZone: IST_TIMEZONE,
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      ...(includeSeconds ? { second: '2-digit' } : {}),
      hour12: true,
    });
    return `${formatted} IST`;
  } catch {
    return '';
  }
};

/**
 * Returns current timestamp formatted in IST
 */
export const getCurrentISTString = (): string => {
  return formatISTDateTime(new Date(), true);
};
