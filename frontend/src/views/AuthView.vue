<template>
  <div class="h-[100dvh] w-full overflow-hidden bg-[#09090b] relative">

    <!-- Ambient glow -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-indigo-500/[0.04] blur-3xl" />
    </div>

    <Transition name="stage" mode="out-in">

      <!-- ─── Stage 1: Splash ─────────────────────────────── -->
      <div
        v-if="stage === 'splash'"
        key="splash"
        class="absolute inset-0 flex flex-col items-center justify-center select-none"
      >
        <!-- Logo idêntica ao AppHeader (dark mode): quadrado branco, N escuro -->
        <div class="logo-appear">
          <div class="w-20 h-20 rounded-2xl bg-white flex items-center justify-center shadow-2xl">
            <span class="text-[#09090b] text-4xl font-bold tracking-tight">N</span>
          </div>
        </div>
        <p class="logo-appear-delayed mt-5 text-white/30 text-[11px] tracking-[0.28em] uppercase font-medium">
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
        class="absolute inset-0 flex flex-col items-center justify-center gap-14 px-6 select-none"
      >
        <!-- Avatar + greeting -->
        <div class="flex flex-col items-center gap-5">
          <div
            class="w-14 h-14 rounded-full bg-gradient-to-br from-slate-700 to-slate-900 border border-slate-600 flex items-center justify-center text-white font-semibold text-base shadow-lg"
            aria-hidden="true"
          >
            {{ currentOwner?.initials }}
          </div>
          <div class="text-center">
            <p class="text-[10px] tracking-widest uppercase text-white/35 mb-1.5">Bem-vindo(a) de volta</p>
            <p class="text-xl font-medium text-white">{{ currentOwner?.name }}</p>
          </div>
        </div>

        <!-- Dots + Numpad -->
        <div class="flex flex-col items-center gap-8">

          <!-- PIN hint -->
          <p class="text-white/35 text-[11px] tracking-wide -mb-2">Digite seu PIN</p>

          <!-- PIN dots -->
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
              class="w-3 h-3 rounded-full border transition-all duration-200"
              :class="pinDotClass(i)"
            />
          </div>

          <!-- Numpad -->
          <div class="grid grid-cols-3 gap-5">
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
                         backdrop-blur-sm
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
                  class="w-16 h-16 rounded-full flex items-center justify-center
                         text-2xl font-light text-white
                         bg-white/5 hover:bg-white/10 active:bg-white/[0.15]
                         backdrop-blur-sm
                         active:scale-90 transition-all duration-100
                         disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
                >
                  {{ key }}
                </button>

              </template>
            </template>
          </div>

          <!-- Biometric button (Face ID / Touch ID) -->
          <div v-if="biometricAvailable" class="flex flex-col items-center gap-2">
            <button
              @click="biometricLogin"
              class="w-12 h-12 rounded-full flex items-center justify-center
                     bg-white/5 hover:bg-white/10 backdrop-blur-sm
                     text-white/40 hover:text-white/75
                     active:scale-90 transition-all duration-100 cursor-pointer"
              aria-label="Entrar com biometria"
            >
              <!-- Fingerprint icon -->
              <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
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
            <span class="text-[10px] text-white/25 tracking-wide">
              {{ hasBiometricCredential(owner) ? 'Face ID · Touch ID' : 'Ativar biometria' }}
            </span>
          </div>

          <!-- Switch profile -->
          <button
            @click="switchProfile"
            class="min-h-[44px] flex items-center justify-center px-6
                   text-white/40 hover:text-white/65
                   text-xs transition-colors duration-200 cursor-pointer"
          >
            Trocar de perfil
          </button>
        </div>
      </div>

    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stage            = ref('splash')
const owner            = ref(null)
const pin              = ref([])
const pinState         = ref('idle')   // 'idle' | 'success' | 'error'
const selectedAvatar   = ref(null)
const biometricAvailable = ref(false)

const CORRECT_PIN = '180621'

const owners = [
  { key: 'alvaro',    name: 'Álvaro',    initials: 'ÁL', gradient: 'from-slate-700 to-slate-900'   },
  { key: 'alexandra', name: 'Alexandra', initials: 'AL', gradient: 'from-violet-500 to-purple-600' },
]

const numpadRows = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9],
  [null, 0, 'del'],
]

const currentOwner = computed(() => owners.find(o => o.key === owner.value))

const pinAriaLabel = computed(() => {
  if (pinState.value === 'success') return 'PIN correto, entrando…'
  if (pinState.value === 'error')   return 'PIN incorreto. Tente novamente.'
  return `${pin.value.length} de 6 dígitos inseridos`
})

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
    // Desktops sem toque (Chrome + Google PW Manager) interceptam o WebAuthn
    // antes de chegar na biometria do SO — esconder nesses casos
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
      // Primeiro uso: registra credencial (dispara Face ID / Touch ID)
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
      // Usos seguintes: verifica com a credencial existente
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
    setTimeout(() => router.push('/'), 900)
  } catch {
    // Usuário cancelou ou dispositivo não suportado — ignora silenciosamente
  }
}

// Dispara Face ID / Touch ID automaticamente ao entrar no vault (se já registrado)
watch(stage, async (newStage) => {
  if (newStage !== 'vault') return
  if (!biometricAvailable.value || !hasBiometricCredential(owner.value)) return
  await new Promise(r => setTimeout(r, 400)) // aguarda transição de tela
  biometricLogin()
})

// ─── Mount / keyboard ────────────────────────────────────────────

onMounted(() => {
  checkBiometricAvailability()

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

function handleKeyboard(e) {
  if (stage.value !== 'vault') return
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
    return filled ? 'bg-indigo-400 border-indigo-400 scale-125' : 'border-indigo-400/20'
  }
  if (pinState.value === 'error') {
    return filled ? 'bg-red-500 border-red-500' : 'border-red-500/30'
  }
  return filled ? 'bg-white border-white' : 'border-slate-500'
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

/* ─── Logo: cresce de ponto minúsculo até tamanho real (efeito mola) ─── */
.logo-appear {
  animation: logo-in 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.logo-appear-delayed {
  animation: logo-in 0.5s 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes logo-in {
  from { opacity: 0; transform: scale(0.08); }
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
