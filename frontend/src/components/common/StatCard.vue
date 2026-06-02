<template>
  <div class="stat-card" :class="[`stat-card--${color}`]" @click="$emit('click')">
    <div class="stat-card__icon">
      <el-icon :size="28">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-card__content">
      <div class="stat-card__value">{{ animatedValue }}</div>
      <div class="stat-card__label">{{ label }}</div>
    </div>
    <div v-if="suffix" class="stat-card__suffix">{{ suffix }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  icon: string
  value: number
  label: string
  color: 'primary' | 'success' | 'warning' | 'danger'
  suffix?: string
}>()

defineEmits(['click'])

const animatedValue = ref(0)

function animateValue(target: number) {
  const duration = 800
  const steps = 30
  const increment = target / steps
  const stepTime = duration / steps
  let current = 0
  let step = 0

  const timer = setInterval(() => {
    step++
    current = Math.round(increment * step)
    if (step >= steps) {
      animatedValue.value = target
      clearInterval(timer)
    } else {
      animatedValue.value = current
    }
  }, stepTime)
}

onMounted(() => {
  animateValue(props.value)
})

watch(() => props.value, (newVal) => {
  animateValue(newVal)
})
</script>

<style lang="scss" scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: $border-radius;
  background: rgba(123, 28, 181, 0.1);
  border: 1px solid $border-color;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    border-radius: 4px 0 0 4px;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }

  &--primary {
    &::before { background: $primary-color; }
    .stat-card__icon { background: rgba(123, 28, 181, 0.2); color: $primary-light; }
  }

  &--success {
    &::before { background: $success-color; }
    .stat-card__icon { background: rgba(38, 198, 218, 0.2); color: $success-color; }
  }

  &--warning {
    &::before { background: $warning-color; }
    .stat-card__icon { background: rgba(255, 179, 0, 0.2); color: $warning-color; }
  }

  &--danger {
    &::before { background: $danger-color; }
    .stat-card__icon { background: rgba(229, 57, 53, 0.2); color: $danger-color; }
  }
}

.stat-card__icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-card__content {
  flex: 1;
}

.stat-card__value {
  font-size: 28px;
  font-weight: 700;
  color: $text-primary;
  line-height: 1.2;
}

.stat-card__label {
  font-size: 13px;
  color: $text-secondary;
  margin-top: 2px;
}

.stat-card__suffix {
  font-size: 14px;
  color: $text-muted;
}
</style>
