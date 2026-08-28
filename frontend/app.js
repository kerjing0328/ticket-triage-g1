const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:7071/api' : '/api';
let tickets = [];
let currentTicketId = null;
let currentPage = 1;
const itemsPerPage = 10;

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

function getFilteredTickets() {
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
    return filtered;
}

function renderPagination(totalItems) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;

    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';
    
    // Previous button
    html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">Previous</button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<span class="page-dots">...</span>`;
        }
    }
    
    // Next button
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next</button>`;
    
    // Page info
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    html += `<span class="page-info">Showing ${start}-${end} of ${totalItems}</span>`;
    
    pagination.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    renderTickets();
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
    const filtered = getFilteredTickets();

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
        renderPagination(0);
        return;
    }

    // Pagination
    const totalPages = Math.ceil(filtered.length / itemsPerPage);
    if (currentPage > totalPages) currentPage = totalPages;
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedTickets = filtered.slice(startIndex, startIndex + itemsPerPage);

    tableBody.innerHTML = paginatedTickets.map(ticket => `
        <tr data-id="${ticket.id}">
            <td><span class="row-id">${ticket.id.substring(0,8)}</span><br><small>${formatDate(ticket.createdAt)}</small></td>
            <td>${escapeHtml(ticket.name)}<br><small>${escapeHtml(ticket.email)}</small></td>
            <td>${escapeHtml(ticket.title)}</td>
            <td>${escapeHtml(ticket.category)}</td>
            <td><span class="badge badge-priority priority-${(ticket.priority || 'medium').toLowerCase()}">${ticket.priority || 'Medium'}</span></td>
            <td><span class="badge ${getStatusClass(ticket.status)}">${ticket.status}</span></td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-primary btn-sm" onclick="openTicketDetail('${ticket.id}')">View</button>
                    <select class="table-select" onchange="openStatusModal('${ticket.id}', this.value)">
                        <option value="New" ${ticket.status === 'New' ? 'selected' : ''}>New</option>
                        <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Resolved" ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                    </select>
                </div>
            </td>
        </tr>
    `).join('');

    renderPagination(filtered.length);
}

function applyFilters() { 
    currentPage = 1;
    renderTickets(); 
}

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
    currentPage = 1;
    renderTickets();
}

function openTicketDetail(ticketId) {
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket) return;

    document.getElementById('detailId').textContent = ticket.id;
    document.getElementById('detailDate').textContent = formatDate(ticket.createdAt);
    document.getElementById('detailStatus').innerHTML = `<span class="badge ${getStatusClass(ticket.status)}">${ticket.status}</span>`;
    document.getElementById('detailPriority').innerHTML = `<span class="badge badge-priority priority-${(ticket.priority || 'medium').toLowerCase()}">${ticket.priority || 'Medium'}</span>`;
    document.getElementById('detailCategory').textContent = ticket.category;
    document.getElementById('detailName').textContent = ticket.name;
    document.getElementById('detailEmail').textContent = ticket.email;
    document.getElementById('detailTitle').textContent = ticket.title;
    document.getElementById('detailDescription').textContent = ticket.description;

    document.getElementById('ticketDetailModal').classList.remove('hidden');
}

function closeDetailModal() {
    document.getElementById('ticketDetailModal').classList.add('hidden');
}

if (document.getElementById('ticketTableBody')) {
    renderTickets();
    document.getElementById('searchEmail')?.addEventListener('input', renderTickets);
    document.getElementById('filterCategory')?.addEventListener('change', renderTickets);
    document.getElementById('filterStatus')?.addEventListener('change', renderTickets);
}
