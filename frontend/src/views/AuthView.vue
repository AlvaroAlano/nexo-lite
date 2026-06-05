<template>
  <div class="h-[100dvh] w-full overflow-hidden bg-[#09090b] relative">

    <!-- Ambient glow -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-emerald-500/[0.05] blur-3xl" />
    </div>

    <Transition name="stage" mode="out-in">

      <!-- ─── Stage 1: Splash ─────────────────────────────── -->
      <div
        v-if="stage === 'splash'"
        key="splash"
        class="absolute inset-0 flex flex-col items-center justify-center select-none"
      >
        <div class="logo-appear">
          <svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="32" cy="32" r="30" stroke="rgba(52,211,153,0.10)" stroke-width="1"/>
            <path d="M20 44 L20 20 L32 36 L44 20 L44 44"
                  stroke="url(#splash-g)" stroke-width="2.5"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="20" cy="20" r="3"   fill="#34d399"/>
            <circle cx="44" cy="20" r="3"   fill="#34d399"/>
            <circle cx="20" cy="44" r="3"   fill="#34d399"/>
            <circle cx="44" cy="44" r="3"   fill="#34d399"/>
            <circle cx="32" cy="36" r="1.8" fill="#34d399" fill-opacity="0.45"/>
            <defs>
              <linearGradient id="splash-g" x1="20" y1="20" x2="44" y2="44" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stop-color="#34d399"/>
                <stop offset="100%" stop-color="#059669"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <p class="logo-appear-delayed mt-4 text-white/30 text-[11px] tracking-[0.28em] uppercase font-medium">
          Nexo Lite
        </p>
      </div>

      <!-- ─── Stage 2: Device Binding ────────────────────── -->
      <div
        v-else-if="stage === 'bind'"
        key="bind"
        class="absolute inset-0 flex flex-col items-center justify-center px-6 gap-12 select-none"
      >
        <div class="text-center space-y-2">
          <h1 class="text-white text-[1.6rem] font-semibold tracking-tight leading-snug">
            De quem é este dispositivo?
          </h1>
          <p class="text-white/40 text-sm">Selecione seu perfil para continuar</p>
        </div>

        <div class="flex gap-4 w-full max-w-xs">
          <button
            v-for="person in owners"
            :key="person.key"
            @click="selectOwner(person.key)"
            class="flex-1 flex flex-col items-center gap-4 py-8 px-4 rounded-2xl border transition-all duration-300 cursor-pointer"
            :class="avatarCardClass(person.key)"
          >
            <!-- Swap by <img> + object-cover when photo available -->
            <div
              class="w-16 h-16 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-[1.05rem] shadow-xl transition-transform duration-300"
              :class="[person.gradient, selectedAvatar === person.key ? 'scale-110' : 'scale-100']"
              aria-hidden="true"
            >
              {{ person.initials }}
            </div>
            <span class="text-[0.85rem] font-medium text-white/75">{{ person.name }}</span>
          </button>
        </div>
      </div>

      <!-- ─── Stage 3: PIN Vault ──────────────────────────── -->
      <div
        v-else-if="stage === 'vault'"
        key="vault"
        class="absolute inset-0 flex flex-col items-center px-6 select-none
               justify-between py-16
               md:justify-center md:gap-14 md:py-0"
      >
        <!-- Avatar + greeting -->
        <div class="flex flex-col items-center gap-4 mt-4 md:mt-0">
          <div
            class="w-14 h-14 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-base shadow-lg"
            :class="currentOwner?.gradient"
            aria-hidden="true"
          >
            {{ currentOwner?.initials }}
          </div>
          <div class="text-center">
            <p class="text-white/35 text-[10px] tracking-[0.22em] uppercase mb-1.5">Bem-vindo(a) de volta</p>
            <p class="text-white text-lg font-semibold">{{ currentOwner?.name }}</p>
          </div>
        </div>

        <!-- Dots + Numpad -->
        <div class="flex flex-col items-center gap-8">

          <!-- PIN hint -->
          <p class="text-white/35 text-[11px] tracking-wide -mb-2">Digite seu PIN</p>

          <!-- PIN dots — aria-live anuncia estado ao leitor de tela -->
          <div
            class="flex gap-4"
            :class="{ shake: pinState === 'error' }"
            role="status"
            aria-live="polite"
            :aria-label="pinAriaLabel"
          >
            <div
              v-for="i in 6"
              :key="i"
              class="w-[14px] h-[14px] rounded-full border-2 transition-all duration-200"
              :class="pinDotClass(i)"
            />
          </div>

          <!-- Numpad -->
          <div class="grid grid-cols-3 gap-3 w-[264px]">
            <template v-for="(row, ri) in numpadRows" :key="ri">
              <template v-for="(key, ci) in row" :key="`${ri}-${ci}`">

                <div v-if="key === null" class="aspect-square" />

                <button
                  v-else-if="key === 'del'"
                  @click="deleteDigit"
                  aria-label="Apagar último dígito"
                  class="aspect-square rounded-full flex items-center justify-center
                         text-white/50 hover:text-white/80
                         bg-white/[0.04] hover:bg-white/[0.08] active:bg-white/[0.13]
                         border border-white/[0.06]
                         active:scale-90 transition-all duration-100 cursor-pointer"
                >
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                       stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 4H8l-7 8 7 8h13a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z"/>
                    <line x1="18" y1="9" x2="12" y2="15"/>
                    <line x1="12" y1="9" x2="18" y2="15"/>
                  </svg>
                </button>

                <button
                  v-else
                  @click="pressDigit(key)"
                  :disabled="pinState !== 'idle' || pin.length >= 6"
                  :aria-label="`Dígito ${key}`"
                  class="aspect-square rounded-full flex items-center justify-center
                         text-white text-xl font-light
                         bg-white/[0.06] hover:bg-white/[0.10] active:bg-white/[0.15]
                         border border-white/[0.07]
                         active:scale-90 transition-all duration-100
                         disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
                >
                  {{ key }}
                </button>

              </template>
            </template>
          </div>

          <!-- Switch profile — min-h-[44px] para touch target correto -->
          <button
            @click="switchProfile"
            class="min-h-[44px] flex items-center justify-center px-6
                   text-white/40 hover:text-white/65
                   text-xs transition-colors duration-200 cursor-pointer"
          >
            Trocar de perfil
          </button>
        </div>

        <!-- Spacer desktop (escondido em md pois usamos gap) -->
        <div class="md:hidden" />
      </div>

    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stage          = ref('splash')
const owner          = ref(null)
const pin            = ref([])
const pinState       = ref('idle')   // 'idle' | 'success' | 'error'
const selectedAvatar = ref(null)

const CORRECT_PIN = '180621'

const owners = [
  { key: 'alvaro',    name: 'Álvaro',    initials: 'ÁL', gradient: 'from-emerald-500 to-teal-600'  },
  { key: 'alexandra', name: 'Alexandra', initials: 'AL', gradient: 'from-violet-500 to-purple-600' },
]

const numpadRows = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9],
  [null, 0, 'del'],
]

const currentOwner = computed(() => owners.find(o => o.key === owner.value))

// Texto descritivo para leitores de tela acompanharem o estado do PIN
const pinAriaLabel = computed(() => {
  if (pinState.value === 'success') return 'PIN correto, entrando…'
  if (pinState.value === 'error')   return 'PIN incorreto. Tente novamente.'
  return `${pin.value.length} de 6 dígitos inseridos`
})

onMounted(() => {
  setTimeout(() => {
    const saved = localStorage.getItem('nexo_owner')
    if (saved) {
      owner.value = saved
      stage.value = 'vault'
    } else {
      stage.value = 'bind'
    }
  }, 1800)

  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
})

// Suporte a teclado físico no desktop
function handleKeyboard(e) {
  if (stage.value !== 'vault') return
  if (e.key >= '0' && e.key <= '9') pressDigit(parseInt(e.key))
  if (e.key === 'Backspace') deleteDigit()
}

function avatarCardClass(key) {
  if (!selectedAvatar.value) {
    return 'bg-white/[0.04] border-white/[0.08] hover:bg-white/[0.07] hover:border-white/[0.15]'
  }
  if (selectedAvatar.value === key) {
    return 'bg-emerald-500/[0.09] border-emerald-500/30 scale-105 cursor-default'
  }
  return 'opacity-0 scale-90 pointer-events-none bg-white/[0.04] border-white/[0.08]'
}

function selectOwner(key) {
  selectedAvatar.value = key
  setTimeout(() => {
    localStorage.setItem('nexo_owner', key)
    owner.value = key
    stage.value = 'vault'
    selectedAvatar.value = null
  }, 500)
}

function vibrate(pattern) {
  try {
    if ('vibrate' in navigator) navigator.vibrate(pattern)
  } catch {}
}

function pressDigit(digit) {
  if (pin.value.length >= 6 || pinState.value !== 'idle') return
  vibrate(40)
  pin.value = [...pin.value, digit]
  if (pin.value.length === 6) validatePin()
}

function deleteDigit() {
  if (pin.value.length === 0 || pinState.value !== 'idle') return
  pin.value = pin.value.slice(0, -1)
}

function validatePin() {
  const entered = pin.value.join('')
  if (entered === CORRECT_PIN) {
    pinState.value = 'success'
    vibrate([30, 50, 30])
    sessionStorage.setItem('nexo_authenticated', '1')
    setTimeout(() => router.push('/'), 900)
  } else {
    pinState.value = 'error'
    vibrate(200)
    setTimeout(() => {
      pin.value = []
      pinState.value = 'idle'
    }, 700)
  }
}

function pinDotClass(position) {
  const filled = position <= pin.value.length
  if (pinState.value === 'success') {
    return filled ? 'bg-emerald-400 border-emerald-400 scale-125' : 'border-emerald-400/20'
  }
  if (pinState.value === 'error') {
    return filled ? 'bg-red-500 border-red-500' : 'border-red-500/30'
  }
  return filled ? 'bg-white border-white' : 'border-white/25'
}

function switchProfile() {
  localStorage.removeItem('nexo_owner')
  owner.value = null
  pin.value = []
  pinState.value = 'idle'
  stage.value = 'bind'
}
</script>

<style scoped>
/* ─── Stage transitions ─── */
.stage-enter-active {
  transition: opacity 0.35s ease, transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.stage-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease-in;
}
.stage-enter-from { opacity: 0; transform: translateY(14px) scale(0.96); }
.stage-leave-to   { opacity: 0; transform: translateY(-8px)  scale(0.98); }

/* ─── Logo entrance (0.5s — dentro do max recomendado de 400-500ms) ─── */
.logo-appear {
  animation: logo-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.logo-appear-delayed {
  animation: logo-in 0.45s 0.12s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes logo-in {
  from { opacity: 0; transform: scale(0.65); }
  to   { opacity: 1; transform: scale(1);    }
}

/* ─── PIN shake ─── */
.shake { animation: pin-shake 0.48s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }

@keyframes pin-shake {
  10%, 90%      { transform: translateX(-3px); }
  20%, 80%      { transform: translateX( 7px); }
  30%, 50%, 70% { transform: translateX(-8px); }
  40%, 60%      { transform: translateX( 8px); }
}

/* ─── Reduz / elimina animações para usuários com preferência de movimento reduzido ─── */
@media (prefers-reduced-motion: reduce) {
  .logo-appear,
  .logo-appear-delayed {
    animation: none;
    opacity: 1;
    transform: none;
  }

  .stage-enter-active,
  .stage-leave-active {
    transition: opacity 0.15s ease;
  }

  .stage-enter-from,
  .stage-leave-to {
    transform: none;
  }

  .shake {
    animation: none;
  }
}
</style>
