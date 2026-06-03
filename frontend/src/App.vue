<template>
  <div class="min-h-full flex flex-col">
    <AppHeader />
    <main class="flex-1 pb-20 md:pb-6 relative overflow-hidden">
      <RouterView v-slot="{ Component, route: r }">
        <Transition :name="transitionName">
          <component :is="Component" :key="r.name" />
        </Transition>
      </RouterView>
    </main>
    <BottomNav class="md:hidden" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import BottomNav from './components/layout/BottomNav.vue'
import { useCategoriesStore } from './stores/categories.js'

const catStore = useCategoriesStore()
onMounted(() => catStore.fetch())

const routeOrder = { dashboard: 0, templates: 1, settings: 2, stats: 3 }
const transitionName = ref('slide-left')
const route = useRoute()

watch(
  () => route.name,
  (to, from) => {
    const toIdx = routeOrder[to] ?? 0
    const fromIdx = routeOrder[from] ?? 0
    transitionName.value = toIdx >= fromIdx ? 'slide-left' : 'slide-right'
  }
)
</script>

<style>
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

/* Leaving view: absolute so it doesn't affect layout height */
.slide-left-leave-active,
.slide-right-leave-active {
  position: absolute;
  inset: 0;
}

.slide-left-enter-from { opacity: 0; transform: translateX(20px); }
.slide-left-leave-to  { opacity: 0; transform: translateX(-20px); }

.slide-right-enter-from { opacity: 0; transform: translateX(-20px); }
.slide-right-leave-to  { opacity: 0; transform: translateX(20px); }
</style>
