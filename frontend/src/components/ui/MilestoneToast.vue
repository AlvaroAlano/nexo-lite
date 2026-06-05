<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="activeMilestone"
        class="fixed left-1/2 -translate-x-1/2 z-[60] font-ss01"
        style="bottom: calc(env(safe-area-inset-bottom, 0px) + 5.5rem)"
      >
        <div class="flex items-center gap-3 px-4 py-3 rounded-2xl bg-brand-ink-light dark:bg-zinc-800 border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.28)] max-w-[320px]">
          <!-- Emoji animado -->
          <span class="text-2xl leading-none select-none" style="animation: bounce-once 0.6s ease 0.1s both">🎉</span>

          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-white leading-tight">Novo marco atingido!</p>
            <p class="text-[11px] text-white/60 mt-0.5 font-tabular">
              Caixinha chegou em
              <span class="text-emerald-400 font-medium">{{ fmtMilestone }}</span>
            </p>
          </div>

          <button
            @click="dismissMilestone"
            class="flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-full text-white/40 hover:text-white hover:bg-white/10 transition-colors"
          >
            <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useGamification } from '../../composables/useGamification.js'

const { activeMilestone, dismissMilestone } = useGamification()

const fmtMilestone = computed(() =>
  (activeMilestone.value ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
)
</script>

<style scoped>
.toast-enter-active { animation: toast-in 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.toast-leave-active { animation: toast-in 0.2s ease-in reverse forwards; }

@keyframes toast-in {
  from { opacity: 0; transform: translateX(-50%) translateY(16px) scale(0.94); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0)    scale(1);    }
}

@keyframes bounce-once {
  0%   { transform: scale(1);    }
  40%  { transform: scale(1.35); }
  70%  { transform: scale(0.9);  }
  100% { transform: scale(1);    }
}
</style>
