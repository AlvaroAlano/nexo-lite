<template>
  <div class="h-[100dvh] w-full overflow-hidden relative bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#0a0a0c] to-black">

    <!-- Ambient glow -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-indigo-500/[0.04] blur-3xl" />
    </div>

    <Transition name="stage" mode="out-in">

      <!-- ─── Stage 1: Entrada (onda neon + cubo Nexo) ─────── -->
      <div
        v-if="stage === 'intro'"
        key="intro"
        @click="skipIntro"
        class="absolute inset-0 flex flex-col items-center justify-center select-none cursor-pointer overflow-hidden"
      >
        <!-- Onda neon de fundo -->
        <div class="intro-wave absolute inset-x-0 top-1/2 -translate-y-1/2 h-48 md:h-64">
          <NeonWave />
        </div>

        <!-- Cubo Nexo + aura -->
        <div class="relative z-10 flex items-center justify-center">
          <!-- Aura radial que floresce uma vez -->
          <div class="intro-aura absolute w-44 h-44 rounded-full pointer-events-none" />
          <!-- Cubo -->
          <div class="intro-logo relative">
            <div class="w-20 h-20 rounded-2xl bg-white flex items-center justify-center shadow-2xl relative overflow-hidden">
              <span class="text-[#09090b] text-4xl font-bold tracking-tight">N</span>
              <!-- Sweep de luz que cruza o logo uma vez -->
              <span class="intro-shine absolute inset-0 pointer-events-none" />
            </div>
          </div>
        </div>

        <!-- Wordmark -->
        <p class="intro-word relative z-10 mt-6 text-white/90 text-base font-semibold tracking-[0.34em] uppercase">
          Nexo Lite
        </p>

        <!-- Hint -->
        <p class="intro-hint absolute bottom-10 text-white/25 text-[10px] tracking-[0.25em] uppercase">
          toque para entrar
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
            <div
              class="w-16 h-16 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-[1.05rem] shadow-xl transition-transform duration-300"
              :class="[person.gradient, selectedAvatar === person.key ? 'scale-110' : 'scale-100']"
            >
              {{ person.initials }}
            </div>
            <span class="text-[0.85rem] font-medium text-white/75">{{ person.name }}</span>
          </button>
        </div>
      </div>

      <!-- ─── Stage 3: Vault ─────────────────────────────── -->
      <div
        v-else-if="stage === 'vault'"
        key="vault"
        class="absolute inset-0 overflow-hidden select-none"
      >
        <Transition :name="vaultTransition" mode="out-in">

          <!-- ── Bio view (default) ────────────────────── -->
          <div
            v-if="!showNumpad"
            key="bio"
            class="absolute inset-0 flex flex-col items-center justify-between px-6"
            :style="safePadding"
          >
            <!-- Top: avatar + name + typewriter -->
            <div class="flex flex-col items-center gap-4 pt-2">
              <div
                class="w-14 h-14 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-semibold text-lg shadow-2xl"
                :class="currentOwner?.gradient"
              >
                {{ currentOwner?.initials }}
              </div>
              <div class="text-center">
                <p class="text-xl font-semibold text-white tracking-tight">{{ currentOwner?.name }}</p>
                <div class="h-6 flex items-center justify-center mt-1">
                  <TypewriterText
                    :text="typewriterPhrases"
                    :speed="75"
                    :delete-speed="35"
                    :delay="2400"
                    :loop="true"
                    class="text-sm text-white/30 font-light tracking-wide"
                  />
                </div>
              </div>
            </div>

            <!-- Middle: biometric button -->
            <div class="flex flex-col items-center gap-5">
              <!-- Pulse rings + button -->
              <div class="relative flex items-center justify-center">
                <span class="absolute inset-0 w-20 h-20 rounded-full border border-white/[0.10] bio-ring-1 pointer-events-none" />
                <span class="absolute inset-0 w-20 h-20 rounded-full border border-white/[0.07] bio-ring-2 pointer-events-none" />
                <button
                  @click="biometricLogin"
                  class="relative w-20 h-20 rounded-full flex items-center justify-center cursor-pointer
                         bg-white/[0.07] border border-white/[0.14]
                         hover:bg-white/[0.11] hover:border-white/[0.22]
                         active:scale-[0.92] transition-all duration-200
                         shadow-[inset_0_1px_0_rgba(255,255,255,0.07)]"
                  :class="pinState === 'success'
                    ? 'bg-emerald-500/20 border-emerald-500/40 shadow-[0_0_32px_rgba(52,211,153,0.18)]'
                    : ''"
                  aria-label="Entrar com biometria"
                >
                  <!-- Success checkmark -->
                  <svg
                    v-if="pinState === 'success'"
                    class="w-8 h-8 text-emerald-400"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <!-- Fingerprint icon -->
                  <svg
                    v-else
                    class="w-9 h-9 text-white/55 transition-colors"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"
                  >
                    <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4"/>
                    <path d="M14 13.12c0 2.38 0 6.38-1 8.88"/>
                    <path d="M17.29 21.02c.12-.6.43-2.3.5-3.02"/>
                    <path d="M2 12a10 10 0 0 1 18-6"/>
                    <path d="M2 16h.01"/>
                    <path d="M21.8 16c.2-2 .131-5.354 0-6"/>
                    <path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2"/>
                    <path d="M8.65 22c.21-.66.45-1.32.57-2"/>
                    <path d="M9 6.8a6 6 0 0 1 9 5.2v2"/>
                  </svg>
                </button>
              </div>
              <p class="text-[11px] text-white/30 tracking-widest uppercase font-medium">
                {{ hasBiometricCredential(owner) ? 'Toque para autenticar' : 'Ativar biometria' }}
              </p>
            </div>

            <!-- Bottom: switch profile — centered -->
            <div class="flex flex-col items-center gap-1 pb-1">
              <button
                @click="switchProfile"
                class="min-h-[44px] flex items-center justify-center px-6
                       text-white/20 hover:text-white/40 text-xs transition-colors duration-200 cursor-pointer"
              >
                Trocar de perfil
              </button>
            </div>

            <!-- Discrete PIN button — bottom right corner -->
            <button
              @click="openNumpad"
              class="absolute bottom-0 right-4 flex items-center gap-1.5 px-3 py-2
                     text-white/15 hover:text-white/35 transition-colors duration-200 cursor-pointer"
              :style="{ paddingBottom: 'max(env(safe-area-inset-bottom, 8px), 8px)' }"
              aria-label="Usar PIN"
            >
              <span class="flex gap-[3px] items-center">
                <span v-for="i in 4" :key="i" class="w-[5px] h-[5px] rounded-full bg-current" />
              </span>
              <span class="text-[10px] tracking-widest font-medium uppercase">PIN</span>
            </button>
          </div>

          <!-- ── PIN view ───────────────────────────────── -->
          <div
            v-else
            key="pin"
            class="absolute inset-0 flex flex-col items-center justify-between px-6"
            :style="safePadding"
          >
            <!-- Back to bio -->
            <div class="w-full flex items-start pt-1">
              <button
                @click="closeNumpad"
                class="flex items-center gap-1.5 text-white/35 hover:text-white/65
                       transition-colors duration-200 text-sm cursor-pointer min-h-[44px]"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="15 18 9 12 15 6"/>
                </svg>
                Biometria
              </button>
            </div>

            <!-- PIN dots + avatar -->
            <div class="flex flex-col items-center gap-6">
              <div class="text-center space-y-0.5">
                <p class="text-[10px] tracking-widest uppercase text-white/30">Digite seu PIN</p>
                <p class="text-lg font-medium text-white/70">{{ currentOwner?.name }}</p>
              </div>
              <div
                class="flex gap-5"
                :class="{ shake: pinState === 'error' }"
                role="status" aria-live="polite" :aria-label="pinAriaLabel"
              >
                <div
                  v-for="i in 4"
                  :key="i"
                  class="w-3 h-3 rounded-full border transition-all duration-200"
                  :class="pinDotClass(i)"
                />
              </div>
            </div>

            <!-- Numpad -->
            <div class="grid grid-cols-3 gap-5 pb-2">
              <template v-for="(row, ri) in numpadRows" :key="ri">
                <template v-for="(key, ci) in row" :key="`${ri}-${ci}`">
                  <div v-if="key === null" class="w-16 h-16" />
                  <button
                    v-else-if="key === 'del'"
                    @click="deleteDigit"
                    aria-label="Apagar último dígito"
                    class="w-16 h-16 rounded-full flex items-center justify-center
                           text-white/50 hover:text-white/80
                           bg-white/5 hover:bg-white/10 active:bg-white/[0.15]
                           backdrop-blur-sm active:scale-90
                           transition-all duration-100 cursor-pointer"
                  >
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 4H8l-7 8 7 8h13a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z"/>
                      <line x1="18" y1="9" x2="12" y2="15"/>
                      <line x1="12" y1="9" x2="18" y2="15"/>
                    </svg>
                  </button>
                  <button
                    v-else
                    @click="pressDigit(key)"
                    :disabled="pinState !== 'idle' || pin.length >= 4"
                    :aria-label="`Dígito ${key}`"
                    class="w-16 h-16 rounded-full flex items-center justify-center
                           text-2xl font-light text-white
                           bg-white/5 hover:bg-white/10 active:bg-white/[0.15]
                           backdrop-blur-sm active:scale-90
                           transition-all duration-100
                           disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
                  >
                    {{ key }}
                  </button>
                </template>
              </template>
            </div>
          </div>

        </Transition>
      </div>

    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCategoriesStore } from '../stores/categories.js'
import TypewriterText from '../components/ui/TypewriterText.vue'
import NeonWave from '../components/ui/NeonWave.vue'

const router = useRouter()

const stage              = ref('intro')
const owner              = ref(null)
const pin                = ref([])
const pinState           = ref('idle')   // 'idle' | 'success' | 'error'
const selectedAvatar     = ref(null)
const biometricAvailable = ref(false)
const showNumpad         = ref(false)
const vaultTransition    = ref('vault-pin-in')

const CORRECT_PIN = '0610'

const owners = [
  { key: 'alvaro',    name: 'Álvaro',    initials: 'ÁL', gradient: 'from-slate-600 to-slate-800'    },
  { key: 'alexandra', name: 'Alexandra', initials: 'AL', gradient: 'from-violet-500 to-purple-700'  },
]

const numpadRows = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9],
  [null, 0, 'del'],
]

const currentOwner = computed(() => owners.find(o => o.key === owner.value))

// Safe area padding for vault views
const safePadding = {
  paddingTop:    'max(env(safe-area-inset-top, 0px), 3.5rem)',
  paddingBottom: 'max(env(safe-area-inset-bottom, 0px), 2rem)',
}

const pinAriaLabel = computed(() => {
  if (pinState.value === 'success') return 'PIN correto, entrando…'
  if (pinState.value === 'error')   return 'PIN incorreto. Tente novamente.'
  return `${pin.value.length} de 4 dígitos inseridos`
})

// ─── Entrada: avança rápido (auto após ~1.7s ou ao toque) ─────────
let introTimer = null

function advanceFromIntro() {
  if (introTimer) { clearTimeout(introTimer); introTimer = null }
  if (stage.value !== 'intro') return
  const saved = localStorage.getItem('nexo_owner')
  if (saved) { owner.value = saved; stage.value = 'vault' }
  else       { stage.value = 'bind' }
}

function skipIntro() {
  advanceFromIntro()
}

// Typewriter phrases — personalized greeting by time of day
const typewriterPhrases = computed(() => {
  const h = new Date().getHours()
  const saudacao = h < 12 ? 'Bom dia' : h < 18 ? 'Boa tarde' : 'Boa noite'
  const nome = currentOwner.value?.name ?? ''
  return [
    `${saudacao}, ${nome}.`,
    'Seus dados, organizados.',
    'Nexo Lite.',
  ]
})

// ─── Numpad show/hide ─────────────────────────────────────────────

function openNumpad() {
  vaultTransition.value = 'vault-pin-in'
  showNumpad.value = true
}

function closeNumpad() {
  vaultTransition.value = 'vault-bio-in'
  showNumpad.value = false
  pin.value = []
  pinState.value = 'idle'
}

// ─── Biometric helpers ────────────────────────────────────────────

function biometricKey(ownerKey) {
  return `nexo_biometric_${ownerKey}`
}

function hasBiometricCredential(ownerKey) {
  return !!localStorage.getItem(biometricKey(ownerKey))
}

function base64UrlToArrayBuffer(base64url) {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/')
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  const binary = atob(base64 + padding)
  const buffer = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) buffer[i] = binary.charCodeAt(i)
  return buffer.buffer
}

async function checkBiometricAvailability() {
  try {
    if (!window.PublicKeyCredential) return
    if (navigator.maxTouchPoints === 0) return
    biometricAvailable.value =
      await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
  } catch {}
}

async function biometricLogin() {
  const ownerKey = owner.value
  const savedId  = localStorage.getItem(biometricKey(ownerKey))

  try {
    if (!savedId) {
      const credential = await navigator.credentials.create({
        publicKey: {
          challenge: crypto.getRandomValues(new Uint8Array(32)),
          rp: { name: 'Nexo Lite' },
          user: {
            id: new TextEncoder().encode(ownerKey),
            name: ownerKey,
            displayName: currentOwner.value?.name ?? ownerKey,
          },
          pubKeyCredParams: [
            { alg: -7,   type: 'public-key' },
            { alg: -257, type: 'public-key' },
          ],
          authenticatorSelection: {
            authenticatorAttachment: 'platform',
            userVerification: 'required',
            residentKey: 'preferred',
          },
          timeout: 60000,
        },
      })
      if (!credential) return
      localStorage.setItem(biometricKey(ownerKey), credential.id)
    } else {
      const assertion = await navigator.credentials.get({
        publicKey: {
          challenge: crypto.getRandomValues(new Uint8Array(32)),
          allowCredentials: [{
            id: base64UrlToArrayBuffer(savedId),
            type: 'public-key',
            transports: ['internal'],
          }],
          userVerification: 'required',
          timeout: 60000,
        },
      })
      if (!assertion) return
    }

    pinState.value = 'success'
    vibrate([30, 50, 30])
    sessionStorage.setItem('nexo_authenticated', '1')
    const catStore = useCategoriesStore()
    catStore.fetch().catch((err) => console.error('Erro ao carregar categorias após biometria:', err))
    setTimeout(() => router.push('/'), 900)
  } catch {
    // Usuário cancelou ou dispositivo não suportado
  }
}

// Auto-trigger biometria ao entrar no vault (se já registrado)
watch(stage, async (newStage) => {
  if (newStage !== 'vault') return
  showNumpad.value = false
  if (!biometricAvailable.value || !hasBiometricCredential(owner.value)) return
  await new Promise(r => setTimeout(r, 450))
  biometricLogin()
})

// ─── Mount / keyboard ────────────────────────────────────────────

onMounted(() => {
  checkBiometricAvailability()
  introTimer = setTimeout(advanceFromIntro, 3200)   // segura para apreciar a entrada (pulável ao toque)
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  if (introTimer) clearTimeout(introTimer)
  window.removeEventListener('keydown', handleKeyboard)
})

function handleKeyboard(e) {
  if (stage.value !== 'vault' || !showNumpad.value) return
  if (e.key >= '0' && e.key <= '9') pressDigit(parseInt(e.key))
  if (e.key === 'Backspace') deleteDigit()
}

// ─── Bind stage ──────────────────────────────────────────────────

function avatarCardClass(key) {
  if (!selectedAvatar.value) {
    return 'bg-white/[0.04] border-white/[0.08] hover:bg-white/[0.07] hover:border-white/[0.15]'
  }
  if (selectedAvatar.value === key) {
    return 'bg-indigo-500/[0.09] border-indigo-500/30 scale-105 cursor-default'
  }
  return 'opacity-0 scale-90 pointer-events-none bg-white/[0.04] border-white/[0.08]'
}

function selectOwner(key) {
  selectedAvatar.value = key
  setTimeout(() => {
    localStorage.setItem('nexo_owner', key)
    owner.value = key
    showNumpad.value = false
    stage.value = 'vault'
    selectedAvatar.value = null
  }, 500)
}

// ─── PIN logic ───────────────────────────────────────────────────

function vibrate(pattern) {
  try {
    if ('vibrate' in navigator) navigator.vibrate(pattern)
  } catch {}
}

function pressDigit(digit) {
  if (pin.value.length >= 4 || pinState.value !== 'idle') return
  vibrate(40)
  pin.value = [...pin.value, digit]
  if (pin.value.length === 4) validatePin()
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
    const catStore = useCategoriesStore()
    catStore.fetch().catch((err) => console.error('Erro ao carregar categorias após PIN:', err))
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
    return filled ? 'bg-indigo-400 border-indigo-400 scale-125' : 'border-indigo-400/20'
  }
  if (pinState.value === 'error') {
    return filled ? 'bg-red-500 border-red-500' : 'border-red-500/30'
  }
  return filled ? 'bg-white border-white' : 'border-slate-500'
}

function switchProfile() {
  localStorage.removeItem('nexo_owner')
  sessionStorage.removeItem('nexo_authenticated')
  owner.value  = null
  pin.value    = []
  pinState.value  = 'idle'
  showNumpad.value = false
  stage.value  = 'bind'

  const catStore = useCategoriesStore()
  catStore.clear()
}
</script>

<style scoped>
/* ─── Stage transitions ─────────────────────────────────────── */
.stage-enter-active {
  transition: opacity 0.35s ease, transform 0.35s var(--ease-out-expo);
}
.stage-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease-in;
}
.stage-enter-from { opacity: 0; transform: translateY(14px) scale(0.96); }
.stage-leave-to   { opacity: 0; transform: translateY(-8px)  scale(0.98); }

/* ─── Vault sub-transitions ──────────────────────────────────── */

/* Bio → PIN: bio exits up, PIN slides in from below */
.vault-pin-in-enter-active {
  transition: opacity 0.32s var(--ease-out-expo),
              transform 0.36s var(--ease-sheet);
}
.vault-pin-in-leave-active {
  position: absolute; inset: 0;
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.vault-pin-in-enter-from { opacity: 0; transform: translateY(32px) scale(0.98); }
.vault-pin-in-leave-to   { opacity: 0; transform: translateY(-12px) scale(0.99); }

/* PIN → Bio: PIN exits down, bio fades in */
.vault-bio-in-enter-active {
  transition: opacity 0.3s var(--ease-out-expo);
}
.vault-bio-in-leave-active {
  position: absolute; inset: 0;
  transition: opacity 0.18s ease, transform 0.22s ease;
}
.vault-bio-in-enter-from { opacity: 0; }
.vault-bio-in-leave-to   { opacity: 0; transform: translateY(18px); }

/* ─── Entrada cinematográfica: aura, cubo (mola+blur), sweep, wordmark, hint ─── */
.intro-wave  { animation: intro-fade 1.1s var(--ease-out-expo) both; }
.intro-aura  {
  animation: intro-aura-bloom 1.8s 0.1s var(--ease-out-expo) both;
  background: radial-gradient(circle, rgba(99,102,241,0.38), rgba(16,185,129,0.12) 45%, transparent 70%);
  filter: blur(14px);
}
.intro-logo  { animation: intro-pop 0.8s 0.12s var(--ease-spring) both; }
.intro-shine {
  animation: intro-shine-sweep 1.1s 0.78s var(--ease-out-expo) both;
  background: linear-gradient(115deg, transparent 38%, rgba(255,255,255,0.95) 50%, transparent 62%);
  transform: translateX(-160%);
}
.intro-word  { animation: intro-word-in 0.9s 0.5s var(--ease-out-expo) both; }
.intro-hint  { animation: intro-fade 0.6s 1.6s var(--ease-out-expo) both; }

@keyframes intro-pop {
  from { opacity: 0; transform: scale(0.5); filter: blur(6px); }
  to   { opacity: 1; transform: scale(1);   filter: blur(0);   }
}
@keyframes intro-aura-bloom {
  0%   { opacity: 0;    transform: scale(0.5);  }
  45%  { opacity: 0.9;  transform: scale(1.05); }
  100% { opacity: 0.55; transform: scale(1);    }
}
@keyframes intro-shine-sweep {
  from { transform: translateX(-160%); }
  to   { transform: translateX(160%);  }
}
@keyframes intro-word-in {
  from { opacity: 0; letter-spacing: 0.12em; transform: translateY(8px); }
  to   { opacity: 1; letter-spacing: 0.34em; transform: translateY(0);   }
}
@keyframes intro-fade {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* ─── Biometric button pulse rings ──────────────────────────── */
@keyframes bio-ring-pulse {
  0%   { transform: scale(1);    opacity: 0.45; }
  100% { transform: scale(2.0);  opacity: 0; }
}
.bio-ring-1 { animation: bio-ring-pulse 2.6s var(--ease-in-out) infinite; }
.bio-ring-2 { animation: bio-ring-pulse 2.6s var(--ease-in-out) infinite; animation-delay: -1.3s; }

/* ─── PIN shake ──────────────────────────────────────────────── */
.shake { animation: pin-shake 0.48s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }

@keyframes pin-shake {
  10%, 90%      { transform: translateX(-3px); }
  20%, 80%      { transform: translateX( 7px); }
  30%, 50%, 70% { transform: translateX(-8px); }
  40%, 60%      { transform: translateX( 8px); }
}

/* ─── Reduced motion ─────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .intro-logo, .intro-wave, .intro-word, .intro-hint { animation: none; opacity: 1; transform: none; filter: none; }
  .intro-aura  { animation: none; opacity: 0.5; transform: none; }
  .intro-shine { animation: none; opacity: 0; }
  .stage-enter-active, .stage-leave-active { transition: opacity 0.15s ease; }
  .stage-enter-from, .stage-leave-to { transform: none; }
  .shake { animation: none; }
  .bio-ring-1, .bio-ring-2 { animation: none; opacity: 0; }
}
</style>
