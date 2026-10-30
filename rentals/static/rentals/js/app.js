let currentBookings = [];
let equipmentList = [];
let selectedBookingId = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    loadEquipment();
    loadBookings();
    bindEvents();
});

function bindEvents() {
    document.getElementById('filter-category').addEventListener('change', loadBookings);
    document.getElementById('filter-status').addEventListener('change', loadBookings);
    
    document.getElementById('live-search').addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        const filtered = currentBookings.filter(b => 
            b.project_title.toLowerCase().includes(q) || 
            b.equipment_detail.name.toLowerCase().includes(q)
        );
        renderBookingsList(filtered);
    });

    const modal = document.getElementById('modal-create');
    document.getElementById('btn-open-modal').addEventListener('click', () => {
        modal.classList.add('show');
    });
    document.getElementById('modal-close-btn').addEventListener('click', () => {
        modal.classList.remove('show');
    });

    document.getElementById('create-booking-form').addEventListener('submit', createBooking);
}

async function loadEquipment() {
    try {
        const res = await fetch('/api/rentals/equipment/');
        if (!res.ok) return;
        equipmentList = await res.json();
        const select = document.getElementById('modal-equipment');
        select.innerHTML = equipmentList.map(eq => 
            `<option value="${eq.id}">${eq.name} [Остаток: ${eq.available_count}/${eq.total_count}]</option>`
        ).join('');
    } catch (e) {
        console.error(e);
    }
}

async function loadBookings() {
    const category = document.getElementById('filter-category').value;
    const status = document.getElementById('filter-status').value;
    
    let url = '/api/rentals/bookings/?';
    if (category) url += `category=${encodeURIComponent(category)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    try {
        const res = await fetch(url);
        if (!res.ok) return;
        currentBookings = await res.json();
        renderBookingsList(currentBookings);
        updateKPIs();
        
        if (selectedBookingId) {
            inspectBooking(selectedBookingId);
        }
    } catch (e) {
        console.error(e);
    }
}

function updateKPIs() {
    document.getElementById('kpi-total').innerText = currentBookings.length;
    const active = currentBookings.filter(b => b.status === 'active' || b.status === 'confirmed').length;
    document.getElementById('kpi-active').innerText = active;

    const availableSum = equipmentList.reduce((acc, eq) => acc + eq.available_count, 0);
    document.getElementById('kpi-available').innerText = availableSum;
}

function renderBookingsList(list) {
    const container = document.getElementById('bookings-container');
    if (!list.length) {
        container.innerHTML = `<div class="empty-msg" style="padding: 40px; text-align: center; color: var(--text-muted); font-family: var(--dot-font);">АКТИВНЫХ БРОНИРОВАНИЙ НЕ НАЙДЕНО</div>`;
        return;
    }

    container.innerHTML = list.map(b => `
        <div class="booking-card ${b.id === selectedBookingId ? 'selected' : ''}" onclick="inspectBooking(${b.id})">
            <div class="booking-thumb">
                <img src="/static/rentals/img/${b.equipment_detail.image_name}" alt="${b.equipment_detail.name}">
            </div>
            <div class="booking-info">
                <div class="booking-top">
                    <span class="booking-title">${b.project_title}</span>
                    <span class="status-pill status-${b.status}">[ ${b.status_display.toUpperCase()} ]</span>
                </div>
                <div class="booking-code">${b.equipment_detail.name} // ${b.equipment_detail.inventory_code}</div>
                <div class="booking-dates">ПЕРИОД: ${b.start_date} -> ${b.end_date} | ОПЕРАТОР: ${b.user_name}</div>
            </div>
        </div>
    `).join('');
}

function inspectBooking(id) {
    selectedBookingId = id;
    const b = currentBookings.find(item => item.id === id);
    if (!b) return;

    renderBookingsList(currentBookings);

    const insp = document.getElementById('inspector-card');
    insp.classList.remove('empty');

    let actions = '';
    if (b.status === 'draft') {
        actions = `
            <button class="btn-glyph highlight" onclick="transitionBooking(${b.id}, 'confirmed')">ПОДТВЕРДИТЬ БРОНЬ (-1 ШТ)</button>
            <button class="btn-glyph text-red" onclick="transitionBooking(${b.id}, 'cancelled')">АННУЛИРОВАТЬ ЧЕРНОВИК</button>
        `;
    } else if (b.status === 'confirmed') {
        actions = `
            <button class="btn-glyph primary" onclick="transitionBooking(${b.id}, 'active')">ВЫДАТЬ НА СЪЕМКУ</button>
            <button class="btn-glyph text-red" onclick="transitionBooking(${b.id}, 'cancelled')">СНЯТЬ БРОНЬ (+1 ШТ)</button>
        `;
    } else if (b.status === 'active') {
        actions = `
            <button class="btn-glyph highlight" onclick="transitionBooking(${b.id}, 'returned')">ПРИНЯТЬ ВОЗВРАТ (+1 ШТ)</button>
        `;
    } else {
        actions = `<span class="timeline-actor">СТАТУС ЗАФИКСИРОВАН // ИЗМЕНЕНИЕ ЗАПРЕЩЕНО</span>`;
    }

    const logsHtml = (b.audit_logs || []).map(log => `
        <div class="timeline-step">
            <div class="timeline-time">${log.timestamp_display}</div>
            <div class="timeline-action">${log.action_type}: ${log.old_status || 'НЕТ'} -> ${log.new_status}</div>
            <div class="timeline-actor">ИНИЦИАТОР: ${log.actor_name} | ${log.comment}</div>
        </div>
    `).join('');

    insp.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h3 style="font-size:18px;">${b.project_title}</h3>
            <button class="btn-glyph text-red" style="padding:4px 8px; font-size:12px;" onclick="deleteBooking(${b.id})">УДАЛИТЬ</button>
        </div>
        <div style="font-size:12px; color:var(--text-muted); margin-bottom:12px; line-height: 1.5;">
            ОБОРУДОВАНИЕ: ${b.equipment_detail.name} [${b.equipment_detail.inventory_code}]<br>
            СТАВКА: ${b.equipment_detail.daily_rate} РУБ / СМЕНА<br>
            ЗАМЕТКИ: ${b.notes || 'Без особых требований'}
        </div>
        <div style="display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap;">
            ${actions}
        </div>
        <div class="section-title">ХРОНОЛОГИЯ // ЖУРНАЛ АУДИТА</div>
        <div class="timeline">
            ${logsHtml || '<div class="timeline-actor">СОБЫТИЙ ПОКА НЕТ</div>'}
        </div>
    `;
}

async function transitionBooking(id, targetStatus) {
    try {
        const res = await fetch(`/api/rentals/bookings/${id}/transition/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ target_status: targetStatus })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(`ОШИБКА БИЗНЕС-ПРАВИЛА: ${data.error || 'Сбой операции'}`);
            return;
        }
        await loadEquipment();
        await loadBookings();
    } catch (e) {
        alert('Сетевая ошибка при изменении статуса');
    }
}

async function createBooking(e) {
    e.preventDefault();
    const banner = document.getElementById('modal-error-banner');
    banner.style.display = 'none';

    const payload = {
        equipment: document.getElementById('modal-equipment').value,
        project_title: document.getElementById('modal-title').value,
        start_date: document.getElementById('modal-start').value,
        end_date: document.getElementById('modal-end').value,
        notes: document.getElementById('modal-notes').value
    };

    try {
        const res = await fetch('/api/rentals/bookings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
            banner.innerText = JSON.stringify(data);
            banner.style.display = 'block';
            return;
        }
        document.getElementById('modal-create').classList.remove('show');
        document.getElementById('create-booking-form').reset();
        await loadEquipment();
        await loadBookings();
        selectedBookingId = data.id;
        inspectBooking(data.id);
    } catch (err) {
        banner.innerText = 'Сетевая ошибка при создании заявки';
        banner.style.display = 'block';
    }
}

async function deleteBooking(id) {
    if (!confirm('Подтверждаете удаление бронирования? Связанный ресурс вернется на склад.')) return;
    try {
        const res = await fetch(`/api/rentals/bookings/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        if (res.status === 204) {
            selectedBookingId = null;
            document.getElementById('inspector-card').innerHTML = '<div class="empty-msg">ВЫБЕРИТЕ ОБЪЕКТ ДЛЯ ПРОСМОТРА</div>';
            document.getElementById('inspector-card').classList.add('empty');
            await loadEquipment();
            await loadBookings();
        }
    } catch (e) {
        alert('Ошибка при удалении');
    }
}