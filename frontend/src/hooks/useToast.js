// S — Single Responsibility: provides showToast() to any component.
import { useApp } from '../context/AppContext'
export const useToast = () => useApp().showToast
