const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:7071/api' : '/api';
let tickets = [];
let currentTicketId = null;

async function createTicketToCloud(ticketData) {
    try {
        const response = await fetch(`${API_BASE}/CreateTicket`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ticketData)
        });
        if (!response.ok) throw new Error('Failed to create ticket.');
        return await response.json();
    } catch (error) {
        console.error("Error creating ticket:", error);
        return null;
    }
}

async function loadTickets() {
    try {
        const response = await fetch(`${API_BASE}/GetTickets`);
        if (!response.ok) throw new Error('Failed to fetch tickets.');
        tickets = await response.json();
    } catch (error) {
        console.error("Error loading tickets:", error);
        tickets = [];
    }
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function getStatusClass(status) {
    const map = {
        'New': 'badge-new',
        'Categorised': 'badge-progress',
        'In Progress': 'badge-progress',
        'Resolved': 'badge-resolved'
    };
    return map[status] || 'badge-new';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Form submission (index.html)
const ticketForm = document.getElementById('ticketForm');
if (ticketForm) {
    ticketForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newTicket = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim(),
            priority: document.getElementById('priority').value
        };
        const result = await createTicketToCloud(newTicket);
        if (result) {
            ticketForm.classList.add('hidden');
            document.getElementById('successMessage').classList.remove('hidden');
            if (result.ticketId) {
                document.getElementById('ticketIdDisplay').textContent = result.ticketId.substring(0, 8);
            }
        } else {
            alert("Error submitting ticket. Please try again.");
        }
    });
}

function resetForm() {
    ticketForm.reset();
    ticketForm.classList.remove('hidden');
    document.getElementById('successMessage').classList.add('hidden');
}

// Admin dashboard (admin.html)
async function renderTickets() {
    await loadTickets();
    const searchEmail = document.getElementById('searchEmail')?.value.toLowerCase() || '';
    const filterCategory = document.getElementById('filterCategory')?.value || '';
    const filterStatus = document.getElementById('filterStatus')?.value || '';

    let filtered = tickets.filter(t => {
        const matchEmail = (t.email || '').toLowerCase().includes(searchEmail);
        const matchCategory = !filterCategory || t.category === filterCategory;
        const matchStatus = !filterStatus || t.status === filterStatus;
        return matchEmail && matchCategory && matchStatus;
    });
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    if (document.getElementById('statTotal')) {
        document.getElementById('statTotal').textContent = tickets.length;
        document.getElementById('statNew').textContent = tickets.filter(t => t.status === 'New').length;
        document.getElementById('statInProgress').textContent = tickets.filter(t => t.status === 'In Progress').length;
        document.getElementById('statResolved').textContent = tickets.filter(t => t.status === 'Resolved').length;
    }

    const tableBody = document.getElementById('ticketTableBody');
    if (!tableBody) return;

    if (filtered.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="muted" style="padding:22px;">No tickets found.</td></tr>';
        return;
    }

    tableBody.innerHTML = filtered.map(ticket => `
        <tr data-id="${ticket.id}">
            <td><span class="row-id">${ticket.id.substring(0,8)}</span><br><small>${formatDate(ticket.createdAt)}</small></td>
            <td>${escapeHtml(ticket.name)}<br><small>${escapeHtml(ticket.email)}</small></td>
            <td>${escapeHtml(ticket.title)}</td>
            <td>${escapeHtml(ticket.category)}</td>
            <td><span class="badge badge-priority priority-${(ticket.priority || 'medium').toLowerCase()}">${ticket.priority || 'Medium'}</span></td>
            <td><span class="badge ${getStatusClass(ticket.status)}">${ticket.status}</span></td>
            <td>
                <div class="table-actions">
                    <select class="table-select" onchange="openStatusModal('${ticket.id}', this.value)">
                        <option value="New" ${ticket.status === 'New' ? 'selected' : ''}>New</option>
                        <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Resolved" ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                    </select>
                </div>
            </td>
        </tr>
    `).join('');
}

function applyFilters() { renderTickets(); }

function openStatusModal(ticketId, newStatus) {
    currentTicketId = ticketId;
    document.getElementById('modalTicketId').textContent = ticketId.substring(0,8);
    document.getElementById('newStatus').value = newStatus;
    document.getElementById('statusModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('statusModal').classList.add('hidden');
    currentTicketId = null;
    renderTickets();
}

async function confirmStatusUpdate() {
    if (!currentTicketId) return;
    const newStatus = document.getElementById('newStatus').value;
    try {
        const response = await fetch(`${API_BASE}/UpdateTicketStatus`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: currentTicketId, status: newStatus })
        });
        if (!response.ok) throw new Error('Failed to update status.');
        closeModal();
        await renderTickets();
    } catch (error) {
        console.error("Error updating ticket:", error);
        alert("Failed to update the ticket status.");
        closeModal();
    }
}

function clearFilters() {
    document.getElementById('searchEmail').value = '';
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterStatus').value = '';
    renderTickets();
}

if (document.getElementById('ticketTableBody')) {
    renderTickets();
    document.getElementById('searchEmail')?.addEventListener('input', renderTickets);
    document.getElementById('filterCategory')?.addEventListener('change', renderTickets);
    document.getElementById('filterStatus')?.addEventListener('change', renderTickets);
}
