const API_BASE = 'http://localhost:8000';

async function apiRequest(endpoint, options = {}) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Ошибка ${res.status}`);
    }
    return await res.json();
}

async function searchByINN() {
    const innInput = document.getElementById("inn-input").value.trim();
    if (!validateINN(innInput)) {
        showToast("Неверный формат ИНН", 'rose');
        return false;
    }

    const existing = getCompany(innInput);
    if (existing) {
        setActiveCompany(innInput);
        populateCompanyScreen(existing); 
        unlockStep(2);    
        updateNavButtons(); 
        navigateTo(2);       
        return existing.data;
    }

    try {
        const response = await fetch(`${API_BASE}/get_company_data/${innInput}`);
        if (!response.ok) throw new Error('Компания не найдена');
        const company = await response.json();

        const added = addCompany(innInput, company);
        setActiveCompany(innInput);
        unlockStep(2);
        populateCompanyScreen(added);
        updateNavButtons();
        navigateTo(2);
    } catch (err) {
        showToast(`Ошибка: ${err.message}`, 'rose');
    }
}

const apiCreateApplication = (data) => apiRequest('/create_application', { method: 'POST', body: JSON.stringify(data) });
const apiPreScoring = (id) => apiRequest(`/create_pre_scoring?application_id=${id}`, { method: 'POST' });
const apiCreateScoringResult = (id) => apiRequest(`/create_scoring_result?application_id=${id}`, { method: 'POST' });
const apiPreScoringAI = (id) => apiRequest(`/create_prescoring_ai?application_id=${id}`, { method: 'POST' });
async function apiUpdateApplication(id, data) {
    const res = await fetch(`${API_BASE}/update_application/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Ошибка ${res.status}`);
    }
    return true; 
}
const apiGetApplicationById = (id) => apiRequest(`/get_application_by_id/${id}`);
const apiGetApplicationsAnalysis = () => apiRequest('/get_applications_analysis');
const apiManagerSummaryAI = (id) => apiRequest(`/create_manager_summary_ai?application_id=${id}`, { method: 'POST' });