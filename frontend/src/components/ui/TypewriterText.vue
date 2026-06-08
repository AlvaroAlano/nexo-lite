<template>
  <span>{{ displayText }}<span class="animate-pulse">{{ cursor }}</span></span>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  text:        { type: [String, Array], required: true },
  speed:       { type: Number, default: 100 },
  cursor:      { type: String, default: '|' },
  loop:        { type: Boolean, default: false },
  deleteSpeed: { type: Number, default: 50 },
  delay:       { type: Number, default: 1500 },
})

const emit = defineEmits(['done'])

const textArray   = computed(() => Array.isArray(props.text) ? props.text : [props.text])
const displayText = ref('')
const charIndex   = ref(0)
const wordIndex   = ref(0)
const deleting    = ref(false)
let timer = null

function tick() {
  const word = textArray.value[wordIndex.value] || ''
  const isLast = wordIndex.value === textArray.value.length - 1

  if (!deleting.value) {
    if (charIndex.value < word.length) {
      displayText.value += word[charIndex.value]
      charIndex.value++
      timer = setTimeout(tick, props.speed)
    } else if (props.loop) {
      // loop: always delete and cycle
      timer = setTimeout(() => { deleting.value = true; tick() }, props.delay)
    } else if (!isLast) {
      // non-loop, more phrases to show: delete and advance
      timer = setTimeout(() => { deleting.value = true; tick() }, props.delay)
    } else {
      // non-loop, last phrase fully typed: emit done and stay
      emit('done')
    }
  } else {
    if (displayText.value.length > 0) {
      displayText.value = displayText.value.slice(0, -1)
      timer = setTimeout(tick, props.deleteSpeed)
    } else {
      deleting.value = false
      charIndex.value = 0
      wordIndex.value = props.loop
        ? (wordIndex.value + 1) % textArray.value.length
        : wordIndex.value + 1
      timer = setTimeout(tick, props.speed)
    }
  }
}

onMounted(() => { timer = setTimeout(tick, props.speed * 3) })
onUnmounted(() => clearTimeout(timer))

watch(() => props.text, () => {
  clearTimeout(timer)
  displayText.value = ''
  charIndex.value = 0
  wordIndex.value = 0
  deleting.value = false
  timer = setTimeout(tick, props.speed)
}, { deep: true })
</script>
