function showUpdateBtn(){
    const btn_update =  document.getElementById('update-btn');
    btn_update.style.display = 'block';
}

function openNotifications() {

    const modal = new bootstrap.Modal(document.getElementById('myModal'));
    const body = document.getElementById('notificationBody');
    body.innerHTML = '<p class="text-muted text-center">Đang tải...</p>';

    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                body.innerHTML = '<p class="text-center text-muted">Không có thông báo</p>';
                return;
            }

            let html = '';
            data.forEach(n => {
                html += `
                    <div class="mb-2 p-2 border rounded ${n.is_read ? '' : 'bg-light'}">
                        <strong>${n.title}</strong>
                        <p class="mb-1">${n.content}</p>
                        <small class="text-muted">${n.ngay_tao}</small>
                    </div>
                `;
            });

            body.innerHTML = html;
        });
        modal.show();
}