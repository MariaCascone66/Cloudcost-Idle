
function openDeleteModal(vmName, deleteUrl, vmId) {
    document.getElementById('vmName').innerText = vmName;
    const form = document.getElementById('deleteForm');
    form.action = deleteUrl;
    form.dataset.vmid = vmId;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function openReactivateModal(vmName, reactivateUrl, vmId) {
    document.getElementById('vmNameReactivate').innerText = vmName;
    const form = document.getElementById('reactivateForm');
    form.action = reactivateUrl;
    form.dataset.vmid = vmId;
    document.getElementById('reactivateModal').classList.remove('hidden');
}

function closeModal(id = 'deleteModal') {
    document.getElementById(id).classList.add('hidden');
}

async function checkVmExists(vmId) {
    const response = await fetch(`/check_vm_exists/${vmId}`);
    const data = await response.json();
    return data.exists;
}

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

    closeModal('deleteModal');

    const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
    if (row) {
        row.remove();
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

async function handleReactivate(event) {
    event.preventDefault();
    const form = document.getElementById('reactivateForm');
    const vmId = form.dataset.vmid;

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
        const statusCell = row.querySelector('td:nth-child(8)');
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

    const deleteForm = document.getElementById('deleteForm');
    const reactivateForm = document.getElementById('reactivateForm');
    if (deleteForm) deleteForm.addEventListener('submit', handleDelete);
    if (reactivateForm) reactivateForm.addEventListener('submit', handleReactivate);
});
