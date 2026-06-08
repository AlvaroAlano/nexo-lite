import { ref } from 'vue'

export function usePullToRefresh(onRefresh) {
  const pullDistance = ref(0)
  const refreshing = ref(false)
  let startY = 0
  let isPulling = false

  function handleTouchStart(e) {
    const scrollEl = document.querySelector('main')
    if (!scrollEl || scrollEl.scrollTop > 0 || refreshing.value) return
    startY = e.touches[0].pageY
    isPulling = true
  }

  function handleTouchMove(e) {
    if (!isPulling || refreshing.value) return
    const diff = e.touches[0].pageY - startY
    if (diff > 0) {
      pullDistance.value = Math.min(diff * 0.4, 60)
      if (pullDistance.value > 10 && e.cancelable) e.preventDefault()
    } else {
      pullDistance.value = 0
      isPulling = false
    }
  }

  async function handleTouchEnd() {
    if (!isPulling) return
    isPulling = false
    if (pullDistance.value >= 45) {
      refreshing.value = true
      pullDistance.value = 45
      try {
        await onRefresh()
      } catch (err) {
        console.error('Erro no pull-to-refresh:', err)
      } finally {
        setTimeout(() => {
          refreshing.value = false
          pullDistance.value = 0
        }, 400)
      }
    } else {
      pullDistance.value = 0
    }
  }

  return { pullDistance, refreshing, handleTouchStart, handleTouchMove, handleTouchEnd }
}
