export const CLOSE_MENUS_EVENT = 'nexo:close-all-menus'

export function broadcastMenuOpen() {
  document.dispatchEvent(new Event(CLOSE_MENUS_EVENT))
}
