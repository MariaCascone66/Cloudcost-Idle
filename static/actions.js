function openDeleteModal(vmName, deleteUrl, vmId) {
    document.getElementById('vmName').innerText = vmName;
    const form = document.getElementById('deleteForm');
    form.action = deleteUrl;
    form.dataset.vmid = vmId;

    resetDeleteModal();
    document.getElementById('deleteModal').classList.remove('hidden');
}

function openReactivateModal(vmName, reactivateUrl, vmId) {
    document.getElementById('vmNameReactivate').innerText = vmName;
    const form = document.getElementById('reactivateForm');
    form.action = reactivateUrl;
    form.dataset.vmid = vmId;

    resetReactivateModal();
    document.getElementById('reactivateModal').classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
    resetDeleteModal();
    resetReactivateModal();
}

function resetDeleteModal() {
    document.getElementById('deleteModalText').innerHTML =
        'Sei sicuro di voler eliminare la VM <span id="vmName" class="font-semibold"></span>? Questa azione è irreversibile.';
    document.getElementById('deleteButtons').classList.remove('justify-center');
    document.getElementById('deleteButtons').innerHTML = `
        <form id="deleteForm" method="POST" onsubmit="handleDelete(event)" data-vmid="">
            <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition">Elimina</button>
        </form>
        <button onclick="closeModal('deleteModal')" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition">Annulla</button>
    `;
}

function resetReactivateModal() {
    document.getElementById('reactivateModalText').innerHTML =
        'Vuoi riattivare la VM <span id="vmNameReactivate" class="font-semibold"></span>?';
    document.getElementById('reactivateButtons').classList.remove('justify-center');
    document.getElementById('reactivateButtons').innerHTML = `
        <form id="reactivateForm" method="POST" onsubmit="handleReactivate(event)" data-vmid="">
            <button type="submit" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition">Riattiva</button>
        </form>
        <button onclick="closeModal('reactivateModal')" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition">Annulla</button>
    `;
}

function showLoadingText(modalId, message) {
    const modalText = document.getElementById(modalId + 'Text');
    modalText.textContent = message;

    const buttons = document.getElementById(modalId + 'Buttons');
    buttons.classList.add('justify-center');
    buttons.innerHTML = `
        <p class="text-gray-600 text-sm flex items-center space-x-2">
            ${message}<span class="dot-anim ml-2 text-lg font-bold animate-pulse">.</span>
        </p>
        <button onclick="closeModal('${modalId}')" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition ml-4">Annulla</button>
    `;
}

async function handleDelete(event) {
    event.preventDefault();
    const form = event.target;
    const vmId = form.dataset.vmid;
    showLoadingText('deleteModal', 'Attendere');

    await fetch(form.action, { method: 'POST' });

    for (let i = 0; i < 10; i++) {
        const exists = await checkVmExists(vmId);
        if (!exists) break;
        await new Promise(r => setTimeout(r, 1000));
    }

    closeModal('deleteModal');
    const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
    if (row) row.remove();
}

async function handleReactivate(event) {
    event.preventDefault();
    const form = event.target;
    const vmId = form.dataset.vmid;
    showLoadingText('reactivateModal', 'Attendere');

    await fetch(form.action, { method: 'POST' });

    for (let i = 0; i < 10; i++) {
        const status = await getVmStatus(vmId);
        if (status === 'ACTIVE') break;
        await new Promise(r => setTimeout(r, 1000));
    }

    await updateVmCost(vmId);

    closeModal('reactivateModal');

    const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
    if (row) {
        const statusCell = row.querySelector('td:nth-child(11)');
        if (statusCell) statusCell.textContent = 'ACTIVE';

        const reactivateBtn = row.querySelector('button.text-green-600');
        if (reactivateBtn) {
            reactivateBtn.classList.add('text-gray-400', 'cursor-not-allowed');
            reactivateBtn.classList.remove('text-green-600', 'hover:underline');
            reactivateBtn.setAttribute('disabled', 'true');
            reactivateBtn.textContent = 'Riattiva';
        }
    }
}

async function updateVmCost(vmId) {
    const response = await fetch(`/get_cost/${vmId}`);
    const data = await response.json();
    if (data.success) {
        const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
        if (row) {
            const costEl = row.querySelector('.vm-cost');
            const uptimeEl = row.querySelector('.vm-uptime');
            if (costEl) costEl.textContent = `$${data.estimated_cost}`;
            if (uptimeEl) uptimeEl.textContent = `${data.uptime} h`;
        }
    }
}

async function getVmStatus(vmId) {
    try {
        const response = await fetch(`/check_vm_status/${vmId}`);
        if (!response.ok) throw new Error("Errore fetch");
        const data = await response.json();
        return data.status;
    } catch (e) {
        console.error("Errore nel recupero dello stato VM:", e);
        return null;
    }
}

async function checkVmExists(vmId) {
    const response = await fetch(`/check_vm_exists/${vmId}`);
    const data = await response.json();
    return data.exists;
}

function startAutoUpdateCosts() {
    const rows = document.querySelectorAll('tr[data-vmid]');
    rows.forEach(row => {
        const vmId = row.dataset.vmid;
        setInterval(() => updateVmCost(vmId), 60000);
        updateVmCost(vmId);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    startAutoUpdateCosts();
});
