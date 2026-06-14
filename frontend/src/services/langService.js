// S — Single Responsibility: all DOM-level language side-effects live here.
// Context calls this service when lang changes — components never touch document directly.

export const langService = {
  apply(lang) {
    document.documentElement.lang = lang
    document.documentElement.dir  = lang === 'ar' ? 'rtl' : 'ltr'
    document.body.classList.toggle('ar', lang === 'ar')
  },
}
