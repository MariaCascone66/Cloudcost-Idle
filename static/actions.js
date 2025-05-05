// Modale eliminazione
function openDeleteModal(vmName, deleteUrl, vmId) {
    const nameSpan = document.getElementById('vmName');
    if (nameSpan) nameSpan.innerText = vmName;
    const form = document.getElementById('deleteForm');
    form.action = deleteUrl;
    form.dataset.vmid = vmId;
    document.getElementById('deleteModal').classList.remove('hidden');
}

// Modale riattivazione
function openReactivateModal(vmName, reactivateUrl, vmId) {
    const nameSpan = document.getElementById('vmNameReactivate');
    if (nameSpan) nameSpan.innerText = vmName;
    const form = document.getElementById('reactivateForm');
    form.action = reactivateUrl;
    form.dataset.vmid = vmId;
    document.getElementById('reactivateModal').classList.remove('hidden');
}

// Chiudi modale
function closeModal(id = 'deleteModal') {
    document.getElementById(id).classList.add('hidden');
}

// Controlla se la VM esiste ancora
async function checkVmExists(vmId) {
    const response = await fetch(`/check_vm_exists/${vmId}`);
    const data = await response.json();
    return data.exists;
}

// Elimina VM
async function handleDelete(event) {
    event.preventDefault();
    const form = document.getElementById('deleteForm');
    const vmId = form.dataset.vmid;

    await fetch(form.action, { method: 'POST' });

    for (let i = 0; i < 10; i++) {
        const exists = await checkVmExists(vmId);
        if (!exists) break;
        await new Promise(r => setTimeout(r, 1000));
    }

    window.location.reload(true);
}

// Ottieni status VM
async function getVmStatus(vmId) {
    const response = await fetch(`/check_vm_status/${vmId}`);
    const data = await response.json();
    return data.status;
}

// Riattiva VM
async function handleReactivate(event) {
    event.preventDefault();
    const form = document.getElementById('reactivateForm');
    const vmId = form.dataset.vmid;

    await fetch(form.action, { method: 'POST' });

    for (let i = 0; i < 15; i++) {
        const status = await getVmStatus(vmId);
        if (status === 'ACTIVE') break;
        await new Promise(r => setTimeout(r, 2000));
    }

    window.location.reload(true);
}

// Aggiornamento automatico dei costi e uptime
function startAutoUpdateCosts() {
    const rows = document.querySelectorAll('[data-vmid]');

    rows.forEach(row => {
        const vmId = row.dataset.vmid;

        async function updateCost() {
            try {
                const res = await fetch(`/get_cost/${vmId}`);
                const data = await res.json();
                if (data.success) {
                    const costEl = row.querySelector('.vm-cost');
                    const uptimeEl = row.querySelector('.vm-uptime');
                    if (costEl) costEl.textContent = `$ ${data.estimated_cost}`;
                    if (uptimeEl) uptimeEl.textContent = `${data.uptime} h`;
                }
            } catch (err) {
                console.warn(`Errore aggiornamento costo VM ${vmId}:`, err);
            }
        }

        updateCost();
        setInterval(updateCost, 60000);
    });
}

document.addEventListener('DOMContentLoaded', startAutoUpdateCosts);
