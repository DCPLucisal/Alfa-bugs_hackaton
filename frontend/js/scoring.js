async function submitToScoring() {
    if (!window.appState.activeCompanyInn || !window.appState.currentGoal) {
        showToast("Выберите компанию и цель", 'rose'); return;
    }
    const activeCompany = getActiveCompany();

    try {
        if (!window.appState.currentApplicationId) {
            const app = await apiCreateApplication({
                client_id: window.appState.clientId,
                company_id: activeCompany.company_id || 1, 
                application_type: 'overdraft',
                amount: window.appState.currentAmount,
                term_value: window.appState.currentTerm,
                term_unit: 'months',
                aim: window.appState.currentGoal,
                status: 'draft',
            });
            window.appState.currentApplicationId = app.id;
            addApplication(window.appState.activeCompanyInn, app.id);
            saveState();
        }
        unlockStep(4); updateNavButtons(); navigateTo(4);
        await runScoringAnimation();
    } catch (err) { showToast(`Ошибка: ${err.message}`, 'rose'); }
}

async function runScoringAnimation() {
    const spinner = document.getElementById('loading-spinner');
    const textContainer = document.getElementById('ai-result-text');
    const btnSend = document.getElementById('btn-send-manager');
    const appId = window.appState.currentApplicationId;

    try {
        const scoring = await apiPreScoring(appId);
        await apiCreateScoringResult(appId);
        const aiResult = await apiPreScoringAI(appId);
        
        window.appState.scoringResult = scoring;
        window.appState.aiExplanation = aiResult.ai_answer_text;
        saveState();

        spinner.classList.add('hidden');
        textContainer.classList.remove('hidden');
        textContainer.innerHTML = `
            <div class="flex items-start gap-3 bg-neutral-900 p-4 rounded-xl border border-neutral-800">
                <i class="fa-solid fa-robot text-alfa-red text-xl mt-1"></i>
                <div>
                    <p class="font-bold text-white mb-1">Совет от ИИ-ассистента:</p>
                    <p>${window.appState.aiExplanation}</p>
                </div>
            </div>
        `;
        btnSend.classList.remove('hidden'); 
    } catch (err) {
        spinner.innerHTML = `<span class="text-rose-400">Ошибка ИИ: ${err.message}</span>`;
    }
}

async function sendToManager() {
    const appId = window.appState.currentApplicationId;
    try {
        await apiUpdateApplication(appId, { status: "validating" });
        unlockStep(5);
        updateNavButtons();
        navigateTo(5); 
    } catch (err) {
        showToast(`Ошибка: ${err.message}`, 'rose');
    }
}