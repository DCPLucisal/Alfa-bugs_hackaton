let currentScreen = 1;

function navigateTo(screenNum) {
    if (!isStepAvailable(screenNum)) {
        showToast("Сначала пройдите предыдущие шаги", 'rose');
        return;
    }
    for (let i = 1; i <= 8; i++) {
        const el = document.getElementById(`screen-${i}`);
        if (el) el.classList.add('hidden');
    }
    const target = document.getElementById(`screen-${screenNum}`);
    if (target) target.classList.remove('hidden');
    
    currentScreen = screenNum;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    updateNavButtons();
    
    if (screenNum === 5) updateCalculator();
    else if (screenNum === 7) checkStatusAndRender();
    else if (screenNum === 8) loadManagerDashboard();
}

async function selectUser(clientId) {
    try {
        window.appState.currentStep = 2; 
        window.appState.currentApplicationId = null;
        window.appState.currentGoal = null;
        window.appState.scoringResult = null;
        window.appState.aiExplanation = null;

        const client = await apiGetClientById(clientId);

        window.appState.clientId = client.id || clientId;
        window.appState.clientName = client.name;
        
        document.getElementById('header-company-name').innerText = `${client.name} ${client.lastname}`;
        document.getElementById('client-greeting').innerText = `Привет, ${client.name}`;
        
        unlockStep(2);
        updateNavButtons();
        navigateTo(2); 
        
        loadClientApplications(); 
        
        try {
            const companies = await apiGetCompaniesByClientId(clientId);
            window.appState.companies = companies.map(c => ({
                inn: c.inn,
                company_id: c.company_id, 
                data: { fns: null, bki: null }
            }));
            saveState();
        } catch(e) {
            console.log("У клиента нет компаний:", e);
            window.appState.companies = [];
            saveState();
        }
        
    } catch (err) {
        showToast(`Ошибка входа: ${err.message}`, 'rose');
    }
}

function startNewApplication() {
    window.appState.currentApplicationId = null;
    window.appState.currentGoal = null;
    window.appState.scoringResult = null;
    window.appState.aiExplanation = null;
    window.appState.currentStep = 3; 
    saveState();


    document.getElementById('inn-input').value = '';
    document.getElementById('inn-error').classList.add('hidden');

    document.querySelectorAll('.goal-tile').forEach(t => {
        t.className = "goal-tile border border-neutral-800 bg-neutral-900/80 hover:bg-neutral-800/80 text-neutral-300 rounded-2xl p-4 text-left transition-all flex flex-col justify-between h-28 space-y-2 focus-gost";
        t.setAttribute('aria-checked', 'false');
        const icon = t.querySelector('i');
        if(icon) icon.className = icon.className.replace(' text-alfa-red', ' text-neutral-400');
    });

    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('hidden');
    spinner.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-2xl"></i> <span class="font-bold text-white">ИИ анализирует данные...</span>`;
    
    const textContainer = document.getElementById('ai-result-text');
    textContainer.classList.add('hidden');
    textContainer.innerHTML = '';
    
    document.getElementById('btn-send-manager').classList.add('hidden');

    document.getElementById('result-container').innerHTML = '';

    const select = document.getElementById('inn-select');
    select.innerHTML = '<option value="">-- Выбрать из списка --</option>';
    
    if (window.appState.companies && window.appState.companies.length > 0) {
        window.appState.companies.forEach(company => {
            const option = document.createElement('option');
            option.value = company.inn;
            option.textContent = `ИНН: ${company.inn}`; 
            select.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.value = "";
        option.textContent = "Нет привязанных компаний";
        option.disabled = true;
        select.appendChild(option);
    }
    
    updateNavButtons();
    navigateTo(3); 
}

function goToCalculator() {
    if (!window.appState.currentGoal) { 
        showToast("Выберите цель", 'rose'); 
        return; 
    }
    unlockStep(5); 
    updateNavButtons(); 
    navigateTo(5); 
}

function selectGoal(tile, goalName) {
    document.querySelectorAll('.goal-tile').forEach(t => {
        t.className = "goal-tile border border-neutral-800 bg-neutral-900/80 text-neutral-300 rounded-2xl p-4 text-left h-28";
    });
    tile.className = "goal-tile border-2 border-alfa-red bg-alfa-red/10 text-white rounded-2xl p-4 text-left h-28";
    window.appState.currentGoal = goalName;                         
    saveState();                                           
}

function isStepAvailable(step) { return step === 1 || step === 8 || step <= window.appState.currentStep; }

function updateNavButtons() {
    for (let i = 1; i <= 8; i++) { 
        const btn = document.getElementById(`nav-btn-${i}`);
        if (!btn) continue;
        if (!isStepAvailable(i)) {
            btn.disabled = true; 
            btn.className = "px-3 py-1.5 rounded-xl text-neutral-600 opacity-50 cursor-not-allowed";
        } else {
            btn.disabled = false; 
            btn.className = i === currentScreen 
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

async function loadClientApplications() {
    const list = document.getElementById('client-apps-list');
    list.innerHTML = '<p class="text-neutral-500 text-sm text-center py-4">Загрузка...</p>';
    
    try {
        const apps = await apiGetUsersApplications(window.appState.clientId);
        if (!apps || apps.length === 0) {
            list.innerHTML = '<p class="text-neutral-500 text-sm text-center py-4">У вас пока нет заявок</p>';
            return;
        }
        
        list.innerHTML = apps.map(app => `
            <div onclick="openExistingApp(${app.application_id || app.id})" class="bg-neutral-900 p-4 rounded-xl border border-neutral-800 cursor-pointer hover:border-alfa-red transition flex justify-between items-center">
                <div>
                    <p class="font-bold text-white">Заявка #${app.application_id || app.id} на ${app.amount.toLocaleString('ru-RU')} ₽</p>
                    <p class="text-xs text-neutral-400">Статус: ${app.status}</p>
                </div>
                <i class="fa-solid fa-chevron-right text-neutral-500"></i>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = `<p class="text-rose-400 text-sm text-center py-4">Ошибка: ${err.message}</p>`;
    }
}

function openExistingApp(appId) {
    window.appState.currentApplicationId = appId;
    saveState();
    unlockStep(7); 
    updateNavButtons();
    navigateTo(7); 
}

