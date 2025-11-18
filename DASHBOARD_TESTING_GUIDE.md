# 🧪 Admin Dashboard - Testing & Usage Guide

## 🚀 Quick Start

### Access the Dashboard
1. **Frontend URL**: `http://localhost:3001/admin`
2. **Credentials**: 
   - Username: `admin`
   - Password: `admin123`

### Prerequisites
- ✅ Frontend running: `npm run dev` (Port 3001)
- ✅ Backend running: `python main_simple.py` or Docker
- ✅ PostgreSQL connected (if using database mode)

---

## 📋 Test Cases

### 1. **Login Page → Admin Dashboard**
```
STEP 1: Navigate to http://localhost:3001/login
STEP 2: Enter credentials
  - Username: admin
  - Password: admin123
STEP 3: Click "Sign In" button
STEP 4: Should redirect to /admin dashboard

EXPECTED: Dashboard loads with all 5 tabs visible and stats populated
```

### 2. **Dashboard Tab - Statistics Cards**
```
STEP 1: Click "Dashboard" tab (should be active by default)
STEP 2: Observe 4 stat cards

EXPECTED RESULTS:
✅ Card 1: "Utilisateurs Actifs" (Cyan gradient)
✅ Card 2: "Examens en Cours" (Emerald gradient)
✅ Card 3: "Sessions Actives" (Amber gradient)
✅ Card 4: "Alertes" (Red gradient)

✅ All cards have:
  - Gradient background with glow effect
  - Animated icons with color
  - Large bold numbers
  - Smooth hover scale effect (1.05x)
```

### 3. **Dashboard Tab - Alerts Section**
```
STEP 1: Scroll down to "Alertes Système" section
STEP 2: Verify alert filter input works

TEST A: No filter
  - Should show all alerts in table
  - Up to 10 rows displayed
  - Empty state shows 📭 if no alerts

TEST B: Filter by student email
  - Enter: "student@test.com"
  - Table filters in real-time
  - Only matching alerts displayed

TEST C: Clear filter
  - Delete text from input
  - All alerts visible again

EXPECTED: Real-time filtering with no lag
```

### 4. **Alert Severity Badges**
```
VERIFY each severity level displays correctly:

Critical:  🔴 CRITIQUE    (Red badge)
High:      🟠 ÉLEVÉ      (Orange badge)
Medium:    🟡 MOYEN      (Yellow badge)
Low:       🔵 BAS        (Blue badge)

EXPECTED: Badges are color-coded and include emoji + text
```

### 5. **Exams Tab - List View**
```
STEP 1: Click "Examens" tab
STEP 2: Verify table displays

EXPECTED:
✅ Table headers: Titre | Description | Durée | Statut | Créé | Actions
✅ Each exam row shows:
  - Title (bold white text)
  - Description (truncated if long)
  - Duration in minutes
  - Status badge (🔴 ACTIF or ⏸️ BROUILLON)
  - Creation timestamp (French locale)

✅ Action buttons (hidden until hover):
  - Edit button (blue-cyan gradient)
  - Delete button (red-rose gradient)

✅ Empty state: 📋 "Aucun examen trouvé"
```

### 6. **Exams Tab - Create Exam Button**
```
STEP 1: Click "Nouvel Examen" button
STEP 2: Observe button styling

EXPECTED: Button is visible with:
✅ Cyan → Blue gradient
✅ + (Plus) icon
✅ "Nouvel Examen" text
✅ Hover effect: brighter gradient + shadow growth
✅ Font-bold styling
```

### 7. **Exams Tab - Delete Exam (CRITICAL TEST)**
```
SETUP: Ensure at least one exam exists in database

STEP 1: Hover over an exam row
STEP 2: Click red delete button (Trash2 icon)
STEP 3: Confirmation dialog appears with warning emoji

DIALOG TEXT SHOULD SHOW:
  "🚨 Êtes-vous CERTAIN de vouloir supprimer cet examen ?
   Cette action est IRRÉVERSIBLE"

STEP 4A: Click "Cancel"
  - Dialog closes
  - Exam remains in table
  - No API call made

STEP 4B: Click "OK"
  - Dialog closes
  - Exam IMMEDIATELY removed from table (optimistic update)
  - DELETE /api/v1/exams/{id} called

BACKEND RESPONSE HANDLING:
  ✅ 200 + {"success": true}
    → UI update already done, success message logged
  
  ❌ 404 Not Found
    → Alert: "❌ Examen introuvable (déjà supprimé?)"
    → Exam still removed from UI
  
  ❌ 503 Service Unavailable
    → Alert: "❌ Erreur serveur : Base de données indisponible"
    → Exam remains in UI (so user can retry)
  
  ❌ Network Error
    → Alert: "❌ Erreur réseau : Impossible de supprimer l'examen"
    → Exam remains in UI

CONSOLE OUTPUT (Open DevTools F12):
  ✅ Success: "✅ Examen {id} supprimé avec succès"
  ❌ Error: "❌ Erreur réseau lors de la suppression: {error}"

EXPECTED: Delete functionality works end-to-end with proper feedback
```

### 8. **Sessions Tab**
```
STEP 1: Click "Sessions" tab

EXPECTED:
✅ Dark theme styling applied
✅ Title: "Gestion des Sessions"
✅ Subtitle: "Surveillance Active"
✅ Placeholder message showing development status
✅ 🔧 Icon visible
✅ "Module en cours de développement" text
✅ "Cette fonctionnalité sera bientôt disponible" subtext
```

### 9. **Settings Tab**
```
STEP 1: Click "Paramètres" tab

EXPECTED:
✅ Dark theme styling applied
✅ Title: "Paramètres Système"
✅ Subtitle: "Configuration Avancée"
✅ Placeholder message showing development status
✅ ⚙️ Icon visible
✅ "Module en cours de développement" text
```

### 10. **Header - Refresh Button**
```
STEP 1: Click circular refresh icon (top-right)
STEP 2: Observe loading behavior

EXPECTED:
✅ Button has hover effect (cyan background)
✅ Stat cards may update if new data available
✅ Tables reload data from backend
✅ No errors in console
```

### 11. **Header - User Section**
```
STEP 1: Verify user info displays
STEP 2: Check user avatar

EXPECTED:
✅ Avatar shows with gradient (green → blue)
✅ Text shows "Administrateur"
✅ Email displays: admin@proctoflex.ai
✅ Glowing effect visible on avatar
```

### 12. **Header - Logout Button**
```
STEP 1: Click red logout button (power icon)
STEP 2: Observe action

EXPECTED:
✅ Auth state cleared (localStorage pf_token removed)
✅ Redirect to /login page
✅ Next admin load requires re-authentication
```

### 13. **Theme Colors - Visual Verification**
```
INSPECT each section for correct colors:

HEADER: Dark slate gradient → Cyan border-bottom
STAT CARDS: Gradient backgrounds with glow
ALERTS TABLE: Red gradient header with red accent border
EXAMS TABLE: Cyan gradient header with cyan accent border
SESSIONS TABLE: Emerald gradient header with cyan accent border
BUTTONS: Consistent gradients (cyan/red/emerald)
TEXT: White headings, cyan/emerald for subtitles
```

### 14. **Responsive Design - Mobile View**
```
STEP 1: Open DevTools (F12)
STEP 2: Toggle Device Toolbar
STEP 3: Select Mobile device (iPhone 12)

EXPECTED:
✅ Stat cards stack vertically (grid-cols-1)
✅ Tables remain scrollable horizontally
✅ Tab buttons scroll if needed
✅ User section hides email on very small screens
✅ All buttons remain clickable
✅ No overflow or layout breaks
```

### 15. **Dark Mode Contrast Check**
```
Using browser accessibility tools:

VERIFY contrast ratios:
✅ Cyan text on dark slate: Valid (contrast > 4.5:1)
✅ White text on slate-800: Valid (contrast > 4.5:1)
✅ Status badges readable (color + emoji + text)

VERIFY color-blindness mode:
✅ Protanopia (Red-blind): Emoji helps identify severity
✅ Deuteranopia (Green-blind): Emoji helps identify severity
✅ Tritanopia (Blue-blind): Text labels backup color
```

---

## 🔍 Browser DevTools Debugging

### Console Checks
```javascript
// Test successful delete (copy-paste in console)
// This simulates what happens:
console.log("✅ Examen 123 supprimé avec succès");

// Test delete error
console.error("❌ Erreur réseau lors de la suppression: Network error");

// Check network requests
// Open Network tab and perform delete
// Should see: DELETE /api/v1/exams/{id} with 200 status
```

### Local Storage Verification
```javascript
// Check authentication token
localStorage.getItem('pf_token')
// Should show: "eyJhbGc..." (JWT token) if logged in

// Clear auth on logout
localStorage.removeItem('pf_token')
// localStorage should be empty after logout
```

### React DevTools
```
1. Install React DevTools extension
2. Open Components tab
3. Search for: AdminDashboard
4. Inspect props:
   - activeTab: 'dashboard' | 'exams' | etc.
   - stats: { activeUsers, activeExams, ... }
   - exams: [ { id, title, status, ... } ]
   - filteredAlerts: [ { id, student, severity, ... } ]
```

---

## 🐛 Troubleshooting

### Issue: Dashboard shows "No data"
```
SOLUTION 1: Check backend is running
  - Backend should be on http://localhost:8000
  - Try: curl http://localhost:8000/docs

SOLUTION 2: Check database connection
  - PostgreSQL should be running
  - Backend logs should show "✅ Connexion à la base de données réussie"

SOLUTION 3: Check CORS headers
  - Open Network tab in DevTools
  - Check /api/v1/users response includes:
    - Access-Control-Allow-Origin: *
    - Access-Control-Allow-Methods: GET, POST, DELETE
```

### Issue: Delete button doesn't work
```
SOLUTION 1: Check network request
  - Open Network tab
  - Click delete button
  - Look for DELETE /api/v1/exams/{id}
  - Status should be 200, 404, or 503 (not 5xx or network error)

SOLUTION 2: Check backend response
  - Should return {"success": true}
  - If 404: exam already deleted, that's ok
  - If 503: database is down

SOLUTION 3: Check browser console for errors
  - F12 → Console tab
  - Should NOT show red error messages
  - Only "✅ Examen {id} supprimé..." or "❌ Erreur..."
```

### Issue: Theme colors not showing
```
SOLUTION 1: Clear browser cache
  - Ctrl + Shift + Delete
  - Clear cache from "beginning of time"
  - Refresh page

SOLUTION 2: Check Tailwind CSS is loaded
  - DevTools → Elements tab
  - Right-click page → Inspect
  - Check <style> tags include Tailwind classes
  - Search for "from-cyan-600" in CSS

SOLUTION 3: Rebuild frontend
  - Stop npm run dev (Ctrl+C)
  - Delete node_modules/.vite
  - npm run build
  - npm run dev
```

### Issue: Filter not working
```
SOLUTION 1: Check input value
  - DevTools → React DevTools
  - Find AdminDashboard component
  - Check studentFilter state value

SOLUTION 2: Check filter logic
  - Console: copy-paste filter code
  - Test with sample data

SOLUTION 3: Check alerts data loaded
  - Verify filteredAlerts array has data
  - Check Network tab shows /api/v1/alerts response
```

---

## ✅ Acceptance Criteria

### Must Have
- [x] Dashboard loads without errors
- [x] Stat cards display with correct values
- [x] Alert filtering works in real-time
- [x] Delete exam removes from table
- [x] Delete shows confirmation dialog
- [x] Logout clears session
- [x] No console errors (only warnings for unused setters)
- [x] All tables display correctly
- [x] Responsive on mobile

### Should Have
- [x] Smooth animations and transitions
- [x] Color-coded status badges
- [x] Hover effects on buttons
- [x] Emoji indicators for visual clarity
- [x] Dark theme applied throughout
- [x] Proper error messages

### Nice to Have
- [x] Glowing effects on cards
- [x] Animated radar icon
- [x] Group hover reveals action buttons
- [x] Striped table rows
- [x] Timestamp in French locale

---

## 🎯 Performance Metrics

### Target Performance
```
Page Load:        < 2 seconds
Filter Response:  < 100ms
Delete Action:    < 500ms (UI)
Animation FPS:    60 FPS (smooth)
Bundle Size:      < 500KB
```

### Check Performance (DevTools)
```
1. Open DevTools → Performance tab
2. Record 5 seconds of interaction
3. Click various tabs and buttons
4. Stop recording
5. Check:
   - Scripting time < 50ms
   - Rendering time < 16ms per frame
   - No long tasks (> 50ms)
```

---

## 📞 Support & Reporting

### Report Issues
If dashboard doesn't work:
1. **Check browser console** (F12 → Console)
2. **Check backend logs** (python main_simple.py output)
3. **Check network requests** (F12 → Network → XHR)
4. **Create issue with**:
   - Browser version
   - Error message
   - Steps to reproduce
   - Screenshots

### Debug Mode
Enable verbose logging:
```javascript
// In browser console
localStorage.setItem('DEBUG_ADMIN_DASHBOARD', 'true');
location.reload();

// Now all actions will log details
```

---

**Testing Status**: ✅ READY FOR QA
**Last Updated**: November 18, 2025
**Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
