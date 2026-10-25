async function submitToScoring() {
    if (!window.appState.activeCompanyInn || !window.appState.currentGoal) {
        showToast("Выберите компанию и цель", 'rose'); return;
    }
    const activeCompany = getActiveCompany();
    if (!activeCompany) {
        showToast("Ошибка: компания не найдена в базе", 'rose'); return;
    }

    try {
        // Если заявка уже есть, обновляем её
        if (window.appState.currentApplicationId) {
            await apiUpdateApplication(window.appState.currentApplicationId, {
                amount: window.appState.currentAmount,
                term_value: window.appState.currentTerm,
                aim: window.appState.currentGoal
            });
        } else {
            // Если нет — создаем новую
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
            saveState();
        }
        
        // Переходим на 6-й экран (Скоринг)
        unlockStep(6); 
        updateNavButtons(); 
        navigateTo(6);
        
        // Запускаем анимацию и запросы
        await runScoringAnimation(); 
    } catch (err) { 
        showToast(`Ошибка при создании заявки: ${err.message}`, 'rose'); 
    }
}

async function runScoringAnimation() {
    const spinner = document.getElementById('loading-spinner');
    const textContainer = document.getElementById('ai-result-text');
    const btnSend = document.getElementById('btn-send-manager');
    const appId = window.appState.currentApplicationId;

    spinner.classList.remove('hidden');
    spinner.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-2xl"></i> <span class="font-bold text-white">ИИ анализирует данные...</span>`;
    textContainer.classList.add('hidden');
    textContainer.innerHTML = '';
    btnSend.classList.add('hidden');

    if (!appId) {
        spinner.innerHTML = `<span class="text-rose-400">Ошибка: ID заявки не найден</span>`;
        return;
    }

    try {
        const scoring = await apiPreScoring(appId);
        window.appState.scoringResult = scoring;

        try {
            await apiUpdateScoringResult(appId);
        } catch (err) {
            console.log("Записи скоринга нет (404), создаем новую...");
            await apiCreateScoringResult(appId);
        }

        const aiResult = await apiPreScoringAI(appId);
        
        window.appState.aiExplanation = aiResult.ai_answer_text;
        saveState();

        spinner.classList.add('hidden');
        textContainer.classList.remove('hidden');
        textContainer.innerHTML = `
            <div class="flex items-start gap-3 bg-neutral-900 p-4 rounded-xl border border-neutral-800">
                <i class="fa-solid fa-robot text-alfa-red text-xl mt-1"></i>
                <div>
                    <p class="font-bold text-white mb-1">Совет от ИИ-ассистента:</p>
                    <p class="text-sm text-neutral-300 leading-relaxed">${window.appState.aiExplanation}</p>
                </div>
            </div>
        `;
        
        btnSend.classList.remove('hidden'); 

    } catch (err) {
        spinner.innerHTML = `<span class="text-rose-400">Ошибка ИИ: ${err.message}</span>`;
        console.error("Ошибка в runScoringAnimation:", err);
    }
}

async function sendToManager() {
    const appId = window.appState.currentApplicationId;
    try {
        await apiUpdateApplication(appId, { status: "validating" });
        unlockStep(7);
        updateNavButtons();
        navigateTo(7); 
    } catch (err) {
        showToast(`Ошибка: ${err.message}`, 'rose');
    }
}