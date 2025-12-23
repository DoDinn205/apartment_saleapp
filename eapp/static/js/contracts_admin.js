window.onload = function() {
    const radioButtons = document.querySelectorAll('input[name="customer_option"]');
    const sectionExisting = document.getElementById('section_existing_customer');
    const sectionNew = document.getElementById('section_new_customer');

    // Chỉ chạy khi trang đó có chứa các phần tử này (tránh lỗi ở trang khác)
    if(sectionExisting && sectionNew) {
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'new') {
                    // Nếu chọn 'Tạo mới' -> Ẩn chọn cũ, Hiện form nhập mới
                    sectionExisting.style.display = 'none';
                    sectionNew.style.display = 'block';

                    // (Tùy chọn) Focus vào ô nhập tên để tiện nhập liệu
                    const nameInput = document.querySelector('input[name="new_name"]');
                    if(nameInput) nameInput.focus();
                } else {
                    // Ngược lại -> Hiện chọn cũ, Ẩn form nhập mới
                    sectionExisting.style.display = 'block';
                    sectionNew.style.display = 'none';
                }
            });
        });
    }

    const extendBtns = document.querySelectorAll('.extendBtn');
        extendBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('extend_id').value = this.getAttribute('data-id');
                document.getElementById('current_date').value = this.getAttribute('data-old-date');
        });
    });

        // Xử lý nút Hủy
    const cancelBtns = document.querySelectorAll('.cancelBtn');
        cancelBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                document.getElementById('cancel_id').value = id;
                document.getElementById('display_cancel_id').innerText = id;
         });
    });

};

