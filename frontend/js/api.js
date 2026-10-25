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
        showToast("Неверный формат ИНН. ИНН содержит 10 или 12 цифр", 'rose');
        return false;
    }

    const existing = getCompany(innInput);
    if (existing && existing.data && existing.data.fns) {
        setActiveCompany(innInput);
        populateCompanyScreen(existing); 
        unlockStep(4);    
        updateNavButtons(); 
        navigateTo(4);       
        return existing.data;
    }

    try {
        const response = await fetch(`${API_BASE}/get_company_data/${innInput}`);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Компания не найдена');
        }
        
        const rawCompany = await response.json();

        const addedCompany = addCompany(innInput, rawCompany);
        
        setActiveCompany(innInput);
        populateCompanyScreen(addedCompany); 
        
        unlockStep(4);
        updateNavButtons();
        navigateTo(4);

        return addedCompany.data;

    } catch (err) {
        showToast(`Ошибка: ${err.message}`, 'rose');
        return null;
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
async function apiUpdateScoringResult(applicationId) {
    const response = await fetch(`${API_BASE}/update_scoringresult/${applicationId}`, {
        method: 'PATCH'
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Ошибка обновления скоринга');
    }
    return await response.json();
}

const apiClientResultAI = (id) => apiRequest(`/create_client_result_ai?application_id=${id}`, { method: 'POST' });
const apiGetUsersApplications = (clientId) => apiRequest(`/get_users_applications/${clientId}`);
const apiGetClientById = (id) => apiRequest(`/get_client_by_id/${id}`);
const apiGetCompaniesByClientId = (id) => apiRequest(`/get_companies_by_client_id/${id}`);