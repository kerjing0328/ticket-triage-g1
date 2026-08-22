const API_BASE = '/api';
let tickets = [];
let currentTicketId = null;

// Generate unique ticket ID
function generateTicketId() {
    return 'TKT-' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substring(2, 6).toUpperCase();
}

// ============================================================
// AZURE FUNCTION: CreateTicket
// Replace localStorage with: fetch(`${API_BASE}/CreateTicket`, { method: 'POST', body: ... })
// Saves ticket to Cosmos DB
// ============================================================
function saveTickets() {
    localStorage.setItem('tickets', JSON.stringify(tickets));
}

// ============================================================
// AZURE FUNCTION: GetTickets
// Replace localStorage with: fetch(`${API_BASE}/GetTickets`)
// Returns ticket array from Cosmos DB
// ============================================================
function loadTickets() {
    const stored = localStorage.getItem('tickets');
    tickets = stored ? JSON.parse(stored) : [];
}

// Get formatted date
function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

// Get status badge class
function getStatusClass(status) {
    const map = {
        'New': 'badge-new',
        'Categorised': 'badge-categorised',
        'In Progress': 'badge-progress',
        'Resolved': 'badge-resolved'
    };
    return map[status] || 'badge-new';
}

// ============================================================
// FORM SUBMISSION
// Calls saveTickets() which uses CreateTicket Azure Function
// Azure Function should also call Azure AI Language to
// auto-categorize the ticket before saving to Cosmos DB
// ============================================================
const ticketForm = document.getElementById('ticketForm');

if (ticketForm) {
    ticketForm.addEventListener('submit', (e) => {
        e.preventDefault();

        loadTickets();

        const newTicket = {
            id: generateTicketId(),
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim(),
            priority: document.getElementById('priority').value,
            category: document.getElementById('category').value,
            status: 'New',
            createdAt: new Date().toISOString()
        };

        tickets.push(newTicket);
        saveTickets();

        document.getElementById('ticketIdDisplay').textContent = newTicket.id;
        ticketForm.classList.add('hidden');
        document.getElementById('successMessage').classList.remove('hidden');
    });
}

function resetForm() {
    ticketForm.reset();
    ticketForm.classList.remove('hidden');
    document.getElementById('successMessage').classList.add('hidden');
}

// ============================================================
// AZURE FUNCTION: GetTickets
// Replace localStorage loadTickets() with:
//   const response = await fetch(`${API_BASE}/GetTickets`);
//   tickets = await response.json();
// Supports query params: ?category=IT+Support&status=New&email=user@example.com
// ============================================================
function renderTickets() {
    loadTickets();

    const searchEmail = document.getElementById('searchEmail')?.value.toLowerCase() || '';
    const filterCategory = document.getElementById('filterCategory')?.value || '';
    const filterStatus = document.getElementById('filterStatus')?.value || '';

    let filtered = tickets.filter(t => {
        const matchEmail = t.email.toLowerCase().includes(searchEmail);
        const matchCategory = !filterCategory || t.category === filterCategory;
        const matchStatus = !filterStatus || t.status === filterStatus;
        return matchEmail && matchCategory && matchStatus;
    });

    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    document.getElementById('statTotal').textContent = tickets.length;
    document.getElementById('statNew').textContent = tickets.filter(t => t.status === 'New').length;
    document.getElementById('statInProgress').textContent = tickets.filter(t => t.status === 'In Progress').length;
    document.getElementById('statResolved').textContent = tickets.filter(t => t.status === 'Resolved').length;

    const listContainer = document.getElementById('ticketList');

    if (filtered.length === 0) {
        listContainer.innerHTML = '<p class="empty-state">No tickets found.</p>';
        return;
    }

    listContainer.innerHTML = filtered.map(ticket => `
        <div class="ticket-card" data-id="${ticket.id}">
            <div class="ticket-header">
                <span class="ticket-id">${ticket.id}</span>
                <span class="badge ${getStatusClass(ticket.status)}">${ticket.status}</span>
                <span class="badge badge-priority priority-${ticket.priority.toLowerCase()}">${ticket.priority}</span>
            </div>
            <h3 class="ticket-title">${escapeHtml(ticket.title)}</h3>
            <div class="ticket-meta">
                <span><strong>From:</strong> ${escapeHtml(ticket.name)} (${escapeHtml(ticket.email)})</span>
                <span><strong>Category:</strong> ${escapeHtml(ticket.category)}</span>
                <span><strong>Created:</strong> ${formatDate(ticket.createdAt)}</span>
            </div>
            <p class="ticket-description">${escapeHtml(ticket.description)}</p>
            <div class="ticket-actions">
                <select class="status-select" onchange="openStatusModal('${ticket.id}', this.value)">
                    <option value="New" ${ticket.status === 'New' ? 'selected' : ''}>New</option>
                    <option value="Categorised" ${ticket.status === 'Categorised' ? 'selected' : ''}>Categorised</option>
                    <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                    <option value="Resolved" ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                </select>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function openStatusModal(ticketId, newStatus) {
    currentTicketId = ticketId;
    document.getElementById('modalTicketId').textContent = ticketId;
    document.getElementById('newStatus').value = newStatus;
    document.getElementById('statusModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('statusModal').classList.add('hidden');
    currentTicketId = null;
}

// ============================================================
// AZURE FUNCTION: UpdateTicketStatus
// Replace localStorage with:
//   await fetch(`${API_BASE}/UpdateTicketStatus`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ id: ticketId, status: newStatus })
//   });
// Updates ticket status in Cosmos DB
// ============================================================
function confirmStatusUpdate() {
    if (!currentTicketId) return;

    const newStatus = document.getElementById('newStatus').value;
    loadTickets();
    const ticket = tickets.find(t => t.id === currentTicketId);
    if (ticket) {
        ticket.status = newStatus;
        saveTickets();
        renderTickets();
    }
    closeModal();
}

function clearFilters() {
    document.getElementById('searchEmail').value = '';
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterStatus').value = '';
    renderTickets();
}

// Initialize admin page
if (document.getElementById('ticketList')) {
    renderTickets();

    document.getElementById('searchEmail')?.addEventListener('input', renderTickets);
    document.getElementById('filterCategory')?.addEventListener('change', renderTickets);
    document.getElementById('filterStatus')?.addEventListener('change', renderTickets);
}
