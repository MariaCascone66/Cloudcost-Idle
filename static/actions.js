// Funzioni per modale di eliminazione
function openDeleteModal(vmName, deleteUrl, vmId) {
    const nameSpan = document.getElementById('vmName');
    if (nameSpan) nameSpan.innerText = vmName;
    const form = document.getElementById('deleteForm');
    form.action = deleteUrl;
    form.dataset.vmid = vmId;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function openReactivateModal(vmName, reactivateUrl, vmId) {
    const nameSpan = document.getElementById('vmNameReactivate');
    if (nameSpan) nameSpan.innerText = vmName;
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

// DELETE
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

// REACTIVATE
async function getVmStatus(vmId) {
    const response = await fetch(`/check_vm_status/${vmId}`);
    const data = await response.json();
    return data.status;
}

async function handleReactivate(event) {
    event.preventDefault();
    const form = document.getElementById('reactivateForm');
    const vmId = form.dataset.vmid;
    await fetch(form.action, { method: 'POST' });

    // Attendi che la VM sia passata ad ACTIVE
    for (let i = 0; i < 15; i++) {
        const status = await getVmStatus(vmId);
        if (status === 'ACTIVE') break;
        await new Promise(r => setTimeout(r, 2000)); // 2s x 15 = max 30s attesa
    }

    window.location.reload(true);
}