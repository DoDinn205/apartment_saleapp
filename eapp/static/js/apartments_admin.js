window.onload = function() {
    const changeApartmentBtn = document.querySelectorAll('.changeApartmentBtn');
    changeApartmentBtn.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
        // Lấy chính xác phần tử nút bấm (dùng currentTarget để xử lý trường hợp click vào icon bên trong)
            const button = event.currentTarget;

            // 3. Lấy dữ liệu từ các thuộc tính data-
            const id = button.getAttribute('data-id');
            const ma = button.getAttribute('data-ma');
            const dientich = button.getAttribute('data-dientich');
            const gia = button.getAttribute('data-gia');
            const typeId = button.getAttribute('data-type');
            const status = button.getAttribute('data-status');

            // 4. Tìm và điền dữ liệu vào các ô input trong Modal
            // (Đảm bảo ID của các ô input này khớp với file HTML modal)
            const idInput = document.getElementById('edit_id');
            const maInput = document.getElementById('edit_ma_can_ho');
            const dtInput = document.getElementById('edit_dien_tich');
            const giaInput = document.getElementById('edit_gia_thue');
            const typeSelect = document.getElementById('edit_type_id');
            const statusSelect = document.getElementById('edit_status');

            if (idInput) idInput.value = id;
            if (maInput) maInput.value = ma;
            if (dtInput) dtInput.value = dientich;
            if (giaInput) giaInput.value = gia;
            if (typeSelect) typeSelect.value = typeId;
            if (statusSelect) statusSelect.value = status;
        });
    });
};