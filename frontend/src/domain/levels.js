// Hệ thống 4 mức cảnh báo — nguồn chân lý duy nhất cho màu/nhãn/thứ tự.
// Đồng bộ với backend (ALERT_LEVEL_PRIORITY) và tiêu chuẩn màu cảnh báo quốc tế.
export const LEVELS = {
  Green: { key: 'Green', label: 'Bình thường', short: 'AN TOÀN', color: '#2E7D32', bg: '#E8F5E9', priority: 0, emoji: '🟢' },
  Yellow: { key: 'Yellow', label: 'Chú ý', short: 'CHÚ Ý', color: '#F9A825', bg: '#FFF8E1', priority: 1, emoji: '🟡' },
  Orange: { key: 'Orange', label: 'Nguy hiểm', short: 'NGUY HIỂM', color: '#EF6C00', bg: '#FFF3E0', priority: 2, emoji: '🟠' },
  Red: { key: 'Red', label: 'Cực kỳ nguy hiểm', short: 'KHẨN CẤP', color: '#C62828', bg: '#FFEBEE', priority: 3, emoji: '🔴' },
}

export const LEVEL_ORDER = ['Red', 'Orange', 'Yellow', 'Green']

export function level(key) {
  return LEVELS[key] || LEVELS.Green
}

export const LANG_LABELS = {
  vi: 'Tiếng Việt',
  thai: 'Tiếng Thái',
  hmong: "Tiếng H'Mông",
}
