# PropManager - Frontend React

Aplicație modernă pentru gestiunea imobilelor și contractelor de închiriere, construită cu React, Tailwind CSS și Lucide React icons.

## 🚀 Tehnologii

- **React 18** - Library UI
- **Vite** - Build tool rapid
- **Tailwind CSS** - Framework CSS utility-first
- **Lucide React** - Iconițe moderne
- **date-fns** - Manipulare date
- **Supabase** - Backend și autentificare

## 📦 Instalare

### 1. Instalează dependințele

```bash
cd frontend
npm install
```

### 2. Configurează variabilele de mediu

Creează un fișier `.env` în folderul `frontend`:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Pornește server-ul de development

```bash
npm run dev
```

Aplicația va rula la: `http://localhost:3000`

## 🎨 Design System

### Culori Principale

- **Primary**: `#2563EB` - Butoane și stări active
- **Navy**: `#1E293B` - Titluri, sidebar, text
- **App-Bg**: `#F8FAFC` - Background pagină
- **Surface**: `#FFFFFF` - Cards, tabele

### Badge-uri Semantice

- **Success**: Bg `#D1FAE5`, Text `#065F46`
- **Warning**: Bg `#FEF3C7`, Text `#92400E`
- **Danger**: Bg `#FEE2E2`, Text `#991B1B`

### Clase Custom Tailwind

```css
/* Butoane */
.btn-primary       /* Buton albastru principal */
.btn-secondary     /* Buton alb cu border */

/* Input-uri */
.input-field       /* Input text standard */
.select-field      /* Select dropdown */

/* Layout */
.card              /* Card alb cu shadow */

/* Badge-uri */
.badge-success     /* Badge verde */
.badge-warning     /* Badge galben */
.badge-danger      /* Badge roșu */

/* Efecte */
.table-row-hover   /* Hover pe rânduri tabel */
.admin-banner      /* Banner info administrator */
```

## 📁 Structură Proiect

```
frontend/
├── public/              # Asset-uri statice
├── src/
│   ├── components/      # Componente reutilizabile
│   │   └── Navbar.jsx   # Navigație top
│   ├── views/           # Pagini principale
│   │   ├── GestiuneImobile.jsx
│   │   ├── GestiuneContracte.jsx
│   │   └── DashboardFiscal.jsx
│   ├── utils/           # Funcții helper
│   ├── hooks/           # Custom React hooks
│   ├── App.jsx          # Componentă principală
│   ├── main.jsx         # Entry point
│   └── index.css        # Stiluri globale + Tailwind
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

## 🎯 Features Implementate

### ✅ Navigație Globală
- Navbar fix în top cu 3 secțiuni
- Logo "PropManager"
- Highlight pentru secțiunea activă

### ✅ Gestiune Portofoliu Imobiliar
- Tabel cu imobile
- Badge pentru procent proprietate (verde 100%, galben <100%)
- Co-proprietari afișați
- Acțiuni: Edit, Șterge

### ✅ Gestiune Contracte
- Formular complet cu 3 secțiuni:
  - **Date Contract**: Imobil, Nr. Contract, Link Document
  - **Date Locatar**: Tip, Nume, CNP/CUI, Telefon, Email, Adresă
  - **Date Financiare**: Chirie, Monedă, Frecvență, Perioada, Nr. Camere
- Tabel contracte cu:
  - Chiriaș (nume + contact)
  - Imobil
  - Chirie (bold, albastru)
  - Valabilitate (cu dată)
  - Status (badge colorat)
  - Acțiuni

### ✅ Dashboard Fiscal
- Statistici principale (venit, contracte, ocupare)
- Placeholder pentru grafice
- Secțiune raport ANAF D212

## 🔧 Comenzi Disponibile

```bash
# Development
npm run dev          # Pornește dev server (http://localhost:3000)

# Build
npm run build        # Build pentru producție

# Preview
npm run preview      # Preview build local

# Lint
npm run lint         # Verifică cod cu ESLint
```

## 📱 Responsive Design

Aplicația este complet responsive:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🎨 Personalizare Tailwind

Toate culorile pot fi modificate în `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      primary: '#2563EB',
      navy: '#1E293B',
      // ...
    }
  }
}
```

## 🔗 Integrare Backend

Pentru a conecta cu backend-ul Python/Supabase:

1. Configurează variabilele de mediu în `.env`
2. Folosește `@supabase/supabase-js` pentru autentificare
3. API calls la backend prin proxy Vite (configurat în `vite.config.js`)

## 📝 Exemple Utilizare

### Adaugă un contract nou

1. Click pe "Adaugă Contract Nou"
2. Completează toate cele 3 secțiuni
3. Click "Salvează Contract"

### Editează un imobil

1. În tabelul imobile, click pe iconița Edit (✏️)
2. Modifică datele
3. Salvează

## 🐛 Troubleshooting

### Eroare la `npm install`
```bash
# Șterge node_modules și reinstalează
rm -rf node_modules package-lock.json
npm install
```

### Tailwind nu aplică stiluri
```bash
# Verifică că ai importat CSS-ul în main.jsx
import './index.css'
```

### Iconițe Lucide nu apar
```bash
# Verifică importurile
import { Building2, FileText } from 'lucide-react';
```

## 📚 Documentație Utile

- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)
- [Supabase](https://supabase.com/docs)

## 🤝 Contribuție

1. Fork repository
2. Creează branch pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit schimbările (`git commit -m 'Add AmazingFeature'`)
4. Push la branch (`git push origin feature/AmazingFeature`)
5. Deschide Pull Request

## 📄 Licență

Acest proiect este proprietate privată.

---

**Versiune:** 3.0.0
**Ultima actualizare:** 2026-01-09
