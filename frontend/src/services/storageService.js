// S — Single Responsibility: all localStorage/sessionStorage access goes here.
// The rest of the app never calls localStorage directly — it calls this service.
// I — Interface Segregation: split into user, lang, draft, result — callers import only what they need.

import { STORAGE_KEYS } from '../constants/storage'

export const userStorage = {
  get:    ()  => JSON.parse(localStorage.getItem(STORAGE_KEYS.USER) || 'null'),
  set:    (u) => localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(u)),
  remove: ()  => localStorage.removeItem(STORAGE_KEYS.USER),
}

export const langStorage = {
  get: ()  => localStorage.getItem(STORAGE_KEYS.LANG) || 'en',
  set: (l) => localStorage.setItem(STORAGE_KEYS.LANG, l),
}

export const draftStorage = {
  get:    ()  => JSON.parse(sessionStorage.getItem(STORAGE_KEYS.DRAFT) || 'null'),
  set:    (d) => sessionStorage.setItem(STORAGE_KEYS.DRAFT, JSON.stringify(d)),
  remove: ()  => sessionStorage.removeItem(STORAGE_KEYS.DRAFT),
}

export const resultStorage = {
  get: ()  => JSON.parse(sessionStorage.getItem(STORAGE_KEYS.RESULT) || 'null'),
  set: (r) => sessionStorage.setItem(STORAGE_KEYS.RESULT, JSON.stringify(r)),
}
