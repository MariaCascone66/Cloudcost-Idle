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

    // Aspetta che la VM venga effettivamente eliminata
    for (let i = 0; i < 10; i++) {
        const exists = await checkVmExists(vmId);
        if (!exists) break;
        await new Promise(r => setTimeout(r, 1000));
    }

    // Chiude la modale
    closeModal('deleteModal');

    // Rimuove la riga dalla tabella
    const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
    if (row) {
        row.remove();
    }
}

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

    // Aspetta che la VM diventi ACTIVE
    for (let i = 0; i < 10; i++) {
        const status = await getVmStatus(vmId);
        if (status === 'ACTIVE') break;
        await new Promise(r => setTimeout(r, 1000));
    }

    // Aggiorna i costi
    await updateVmCost(vmId);

    // Chiude la modale
    closeModal('reactivateModal');

    // Aggiorna lo stato nella tabella
    const row = document.querySelector(`tr[data-vmid="${vmId}"]`);
    if (row) {
        const statusCell = row.querySelector('td:nth-child(8)');
        if (statusCell) statusCell.textContent = 'ACTIVE';

        // Disabilita il bottone Riattiva
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

async function fetchIdleVMs() {
    const response = await fetch("/api/idle_vms");
    const vms = await response.json();

    const tbody = document.getElementById("idle-vm-body");
    tbody.innerHTML = "";

    if (vms.length === 0) {
        tbody.innerHTML = `<tr>
            <td colspan="3" class="px-4 py-2 text-center text-gray-500">No idle instances found.</td>
        </tr>`;
        return;
    }

    for (const vm of vms) {
        const row = document.createElement("tr");
        row.className = "hover:bg-gray-50";

        row.innerHTML = `
            <td class="px-4 py-2 font-medium">${vm.instance_name}</td>
            <td class="px-4 py-2">${vm.hours_since_last_update}</td>
            <td class="px-4 py-2">
                <button onclick="openReactivateModal('${vm.instance_name}', '/reactivate_vm/${vm.id}', '${vm.id}')" class="text-green-600 hover:underline">Riattiva</button>
                <br>
                <button onclick="openDeleteModal('${vm.instance_name}', '/delete_idle_vm/${vm.id}', '${vm.id}')" class="text-red-600 hover:underline mt-2">Elimina</button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

// Esegui all'avvio e ogni 30 secondi
fetchIdleVMs();
setInterval(fetchIdleVMs, 30000);

function startAutoUpdateCosts() {
    const rows = document.querySelectorAll('tr[data-vmid]');
    rows.forEach(row => {
        const vmId = row.dataset.vmid;
        setInterval(() => updateVmCost(vmId), 60000); // ogni 60 secondi
        updateVmCost(vmId); // prima esecuzione
    });
}

document.addEventListener('DOMContentLoaded', startAutoUpdateCosts);

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
