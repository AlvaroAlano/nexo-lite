import {
  Home, Car, Utensils, Gamepad2, Heart, Smartphone,
  CreditCard, GraduationCap, Briefcase, ShoppingBag,
  Zap, Wallet, PawPrint, Plane, Gift, Package,
  Wrench, Coffee, Music, Dumbbell, Tv, Bus,
  Building2, Scissors, BookOpen, Baby, Shirt,
  Fuel, Wifi, ShieldCheck,
} from 'lucide-vue-next'

// Icon registry: key (stored in DB) → { component, label }
export const CATEGORY_ICONS = [
  { key: 'Home',        component: Home,        label: 'Moradia'      },
  { key: 'Car',         component: Car,         label: 'Carro'        },
  { key: 'Utensils',    component: Utensils,    label: 'Alimentação'  },
  { key: 'ShoppingBag', component: ShoppingBag, label: 'Compras'      },
  { key: 'CreditCard',  component: CreditCard,  label: 'Cartão'       },
  { key: 'Wallet',      component: Wallet,      label: 'Finanças'     },
  { key: 'Heart',       component: Heart,       label: 'Saúde'        },
  { key: 'Dumbbell',    component: Dumbbell,    label: 'Academia'     },
  { key: 'Pill',        component: ShieldCheck, label: 'Remédio'      },
  { key: 'Smartphone',  component: Smartphone,  label: 'Celular'      },
  { key: 'Wifi',        component: Wifi,        label: 'Internet'     },
  { key: 'Zap',         component: Zap,         label: 'Energia'      },
  { key: 'Fuel',        component: Fuel,        label: 'Combustível'  },
  { key: 'Bus',         component: Bus,         label: 'Transporte'   },
  { key: 'Plane',       component: Plane,       label: 'Viagem'       },
  { key: 'Gamepad2',    component: Gamepad2,    label: 'Lazer'        },
  { key: 'Music',       component: Music,       label: 'Música'       },
  { key: 'Tv',          component: Tv,          label: 'Streaming'    },
  { key: 'Coffee',      component: Coffee,      label: 'Café'         },
  { key: 'GraduationCap', component: GraduationCap, label: 'Educação' },
  { key: 'BookOpen',    component: BookOpen,    label: 'Livros'       },
  { key: 'Briefcase',   component: Briefcase,   label: 'Trabalho'     },
  { key: 'Building2',   component: Building2,   label: 'Empresa'      },
  { key: 'Wrench',      component: Wrench,      label: 'Manutenção'   },
  { key: 'Shirt',       component: Shirt,       label: 'Roupas'       },
  { key: 'Scissors',    component: Scissors,    label: 'Estética'     },
  { key: 'Baby',        component: Baby,        label: 'Filhos'       },
  { key: 'PawPrint',    component: PawPrint,    label: 'Pets'         },
  { key: 'Gift',        component: Gift,        label: 'Presentes'    },
  { key: 'Package',     component: Package,     label: 'Outros'       },
]

const ICON_MAP = Object.fromEntries(CATEGORY_ICONS.map(i => [i.key, i]))

export function getIconComponent(key) {
  return ICON_MAP[key]?.component ?? Package
}

export function getIconLabel(key) {
  return ICON_MAP[key]?.label ?? key
}

// Color palette — key stored in DB, used to compute inline styles
export const COLORS = [
  { key: 'slate',   bg: '#64748b', light: '#f1f5f9', text: '#334155' },
  { key: 'red',     bg: '#ef4444', light: '#fef2f2', text: '#991b1b' },
  { key: 'orange',  bg: '#f97316', light: '#fff7ed', text: '#9a3412' },
  { key: 'amber',   bg: '#f59e0b', light: '#fffbeb', text: '#92400e' },
  { key: 'lime',    bg: '#84cc16', light: '#f7fee7', text: '#3f6212' },
  { key: 'emerald', bg: '#10b981', light: '#ecfdf5', text: '#065f46' },
  { key: 'teal',    bg: '#14b8a6', light: '#f0fdfa', text: '#134e4a' },
  { key: 'blue',    bg: '#3b82f6', light: '#eff6ff', text: '#1e3a8a' },
  { key: 'indigo',  bg: '#6366f1', light: '#eef2ff', text: '#312e81' },
  { key: 'violet',  bg: '#8b5cf6', light: '#f5f3ff', text: '#4c1d95' },
  { key: 'pink',    bg: '#ec4899', light: '#fdf2f8', text: '#831843' },
  { key: 'rose',    bg: '#f43f5e', light: '#fff1f2', text: '#881337' },
]

const COLOR_MAP = Object.fromEntries(COLORS.map(c => [c.key, c]))

export function colorByKey(key) {
  return COLOR_MAP[key] ?? COLOR_MAP.slate
}
