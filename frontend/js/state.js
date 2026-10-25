window.appState = {
    clientId: 1,
    clientName: null,
    currentStep: 1,
    activeCompanyInn: null,
    companies: [],
    currentApplicationId: null,
    currentAmount: 3000000,
    currentGoal: null,
    currentTerm: 24,
    aiExplanation: null,
    scoringResult: null
    
};

function saveState() {
    localStorage.setItem('appState', JSON.stringify(window.appState));
}

function loadState() {
    const saved = localStorage.getItem('appState');
    if (saved) {
        try { Object.assign(window.appState, JSON.parse(saved)); } 
        catch (e) { console.error('Ошибка восстановления', e); }
    }
}

function unlockStep(step) {
    if (window.appState.currentStep < step) {
        window.appState.currentStep = step;
        saveState();
    }
}

function addCompany(inn, data) {
    const existing = window.appState.companies.find(c => c.inn == inn);
    if (existing) {
        existing.data = { bki: data.bki_data, fns: data.fns_data };
        if (data.company_id) existing.company_id = data.company_id;
        saveState();
        return existing;
    }
    const newCompany = {
        inn: inn,
        company_id: data.company_id,
        data: { bki: data.bki_data, fns: data.fns_data }
    };
    window.appState.companies.push(newCompany);
    saveState();
    return newCompany;
}

function getCompany(inn) { return window.appState.companies.find(c => c.inn == inn) || null; }
function setActiveCompany(inn) { 
    if (getCompany(inn)) { window.appState.activeCompanyInn = inn; saveState(); return true; } 
    return false; 
}
function getActiveCompany() { return getCompany(window.appState.activeCompanyInn); }
function addApplication(inn, appId) {
    const c = getCompany(inn);
    if (c && !c.applications.includes(appId)) { c.applications.push(appId); saveState(); }
}