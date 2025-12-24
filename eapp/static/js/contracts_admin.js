window.onload = function() {
    const radioButtons = document.querySelectorAll('input[name="customer_option"]');
    const sectionExisting = document.getElementById('section_existing_customer');
    const sectionNew = document.getElementById('section_new_customer');


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

    const select_apm = document.getElementById('select_apm');
    const input_gia_thue = document.getElementById('input_gia_thue');
    select_apm.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];

            // Lấy giá trị từ thuộc tính data-price mà ta đã gán ở Bước 1
            const price = selectedOption.getAttribute('data-price');

            // 3. Cập nhật giá trị vào ô nhập liệu
            if (price) {
                // Chuyển về dạng số nguyên (bỏ số thập phân .0 nếu có) để đẹp form
                input_gia_thue.value = Math.floor(parseFloat(price));
            } else {
                input_gia_thue.value = ''; // Xóa trắng nếu chọn dòng mặc định
            }
    });

    const addMemberModal = document.getElementById('addMemberModal');
    addMemberModal.addEventListener('show.bs.modal', event => {
        // Nút bấm kích hoạt modal
        const button = event.relatedTarget;
        // Lấy ID hợp đồng từ data-id
        const contractId = button.getAttribute('data-id');
        // Gán vào input ẩn
        addMemberModal.querySelector('#member_contract_id_hidden').value = contractId;
    });




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

