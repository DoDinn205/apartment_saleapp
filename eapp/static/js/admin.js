window.onload = function() {
            // Tìm tất cả các thông báo (alert) đang hiện
            var alerts = document.querySelectorAll('.alert');

            alerts.forEach(function(alert) {
                // Đặt hẹn giờ: 4000ms = 4 giây
                setTimeout(function() {
                    // Dùng Bootstrap API để đóng thông báo (có hiệu ứng mờ dần)
                    var bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 4000);
            });
};

//Xử lý khi nhấn vào các mục menu (li)
//const menuItems = document.querySelectorAll(".sidebar ul li");
//
//menuItems.forEach(item => {
//    item.addEventListener('click', function () {
//        // Tìm và xóa class active của mục cũ (nếu có)
//        const activeItem = document.querySelector(".sidebar ul li.active");
//        if (activeItem) {
//            activeItem.classList.remove('active');
//        }
//        // Thêm class active vào mục vừa nhấn
//        this.classList.add('active');
//    });
//});

