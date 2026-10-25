let currentScreen = 1;

function navigateTo(screenNum) {
    if (!isStepAvailable(screenNum)) {
        showToast("Сначала пройдите предыдущие шаги", 'rose');
        return;
    }
    for (let i = 1; i <= 6; i++) document.getElementById(`screen-${i}`).classList.add('hidden');
    document.getElementById(`screen-${screenNum}`).classList.remove('hidden');
    currentScreen = screenNum;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    updateNavButtons();
    
    if (screenNum === 3) updateCalculator();
    else if (screenNum === 5) checkStatusAndRender();
    else if (screenNum === 6) loadManagerDashboard();
}

function loginWithAlfa() {
    const testInn = "7701234567";
    if (!getCompany(testInn)) {
        addCompany(testInn, {
            company_id: 1,
            fns_data: { name: "ООО «Ромашка»", inn: testInn, okved: "46.90", status: "active", registration_date: "2019-03-12" },
            bki_data: { found_in_bki: true, overdue_count_12m: 0 }
        });
    }
    setActiveCompany(testInn);
    unlockStep(2); updateNavButtons(); populateCompanyScreen(getCompany(testInn)); navigateTo(2);
}

function goToCalculator() {
    if (!window.appState.currentGoal) { showToast("Выберите цель", 'rose'); return; }
    unlockStep(3); updateNavButtons(); navigateTo(3);      
}

function selectGoal(tile, goalName) {
    document.querySelectorAll('.goal-tile').forEach(t => {
        t.className = "goal-tile border border-neutral-800 bg-neutral-900/80 text-neutral-300 rounded-2xl p-4 text-left h-28";
    });
    tile.className = "goal-tile border-2 border-alfa-red bg-alfa-red/10 text-white rounded-2xl p-4 text-left h-28";
    window.appState.currentGoal = goalName;                         
    saveState();                                           
}

function isStepAvailable(step) { return step === 1 || step === 6 || step <= window.appState.currentStep; }

function updateNavButtons() {
    for (let i = 1; i <= 6; i++) {
        const btn = document.getElementById(`nav-btn-${i}`);
        if (!btn) continue;
        if (!isStepAvailable(i)) {
            btn.disabled = true; btn.className = "px-3 py-1.5 text-neutral-600 opacity-50 cursor-not-allowed";
        } else {
            btn.disabled = false; btn.className = i === currentScreen 
                ? "px-3 py-1.5 rounded-xl bg-alfa-red text-white shadow focus-gost" 
                : "px-3 py-1.5 rounded-xl text-neutral-400 hover:text-white focus-gost";
        }
    }
}

function populateCompanyScreen(company) {
    const fns = company.data.fns;  
    document.getElementById('company-name').innerText = fns.name || '—';
    document.getElementById('company-inn').innerText = fns.kpp ? `${company.inn} / ${fns.kpp}` : company.inn;
    document.getElementById('company-okved').innerText = fns.okved || '—';
    if (fns.registration_date) {
        const regDate = new Date(fns.registration_date);
        document.getElementById('company-date').innerText = regDate.toLocaleDateString('ru-RU');
    }
}