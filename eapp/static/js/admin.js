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

