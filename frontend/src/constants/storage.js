// S — Single Responsibility: one file owns all storage key names.
// Changing a key name means changing it in exactly one place.
export const STORAGE_KEYS = {
  USER:          'ist_user',
  ACCESS_TOKEN:  'ist_access_token',
  REFRESH_TOKEN: 'ist_refresh_token',
  LANG:          'ist_lang',
  DRAFT:         'ist_draft',
  RESULT:        'ist_result',
}
