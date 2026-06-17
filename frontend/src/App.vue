<template>
  <div class="h-[100dvh] w-full flex flex-col overflow-hidden relative">
    <AppHeader v-if="!isAuth" class="flex-shrink-0 z-50" />

    <main
      class="flex-1 overflow-y-auto overflow-x-hidden w-full relative"
      :class="isAuth ? '' : 'pb-28'"
    >
      <RouterView v-slot="{ Component, route: r }">
        <Transition :name="transitionName">
          <component :is="Component" :key="r.name" />
        </Transition>
      </RouterView>
    </main>

    <BottomNav v-if="!isAuth" />
    <MilestoneToast v-if="!isAuth" />
    <LoanModal v-if="!isAuth" />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import BottomNav from './components/layout/BottomNav.vue'
import MilestoneToast from './components/ui/MilestoneToast.vue'
import LoanModal from './components/modals/LoanModal.vue'

const routeOrder = { dashboard: 0, templates: 1, settings: 2, stats: 3 }
const transitionName = ref('slide-left')
const route = useRoute()
const isAuth = computed(() => route.name === 'auth')

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
/* Enter: ease-out-expo — snappy deceleration, graceful landing */
.slide-left-enter-active,
.slide-right-enter-active {
  transition: opacity 220ms cubic-bezier(0.22, 1, 0.36, 1),
              transform 220ms cubic-bezier(0.22, 1, 0.36, 1);
}

/* Leave: ease-in — quick, clean departure */
.slide-left-leave-active,
.slide-right-leave-active {
  position: absolute;
  inset: 0;
  transition: opacity 160ms cubic-bezier(0.4, 0, 1, 1),
              transform 160ms cubic-bezier(0.4, 0, 1, 1);
}

.slide-left-enter-from  { opacity: 0; transform: translateX(14px) scale(0.99); }
.slide-left-leave-to    { opacity: 0; transform: translateX(-14px) scale(0.99); }

.slide-right-enter-from { opacity: 0; transform: translateX(-14px) scale(0.99); }
.slide-right-leave-to   { opacity: 0; transform: translateX(14px) scale(0.99); }
</style>
