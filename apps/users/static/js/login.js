$(document).ready(function() {
  $("#login-form").validate({
    errorClass: "is-invalid",
    validClass: "is-valid",
    errorElement: "div",
    onfocusout: function(elem) { this.element(elem); },
    errorPlacement: function(error, element) {
      error.addClass("invalid-feedback");

      if (element.attr("id") === "phone") {
        // 把錯誤訊息放在 intl-tel-input 容器後
        element.closest(".intl-tel-input").after(error);
      } else {
        element.after(error);
      }
    },

    rules: {
      username: { required: true },
      password: {
        required: true
      }
    },
    messages: {
      username: { required: "請輸入使用者名稱" },
      password: {
        required: "請輸入密碼",
        minlength: "密碼至少需 6 個字元"
      }
    }
  });
});