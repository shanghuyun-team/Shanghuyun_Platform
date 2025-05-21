$(function() {
  $("#register-form").validate({
    errorClass: "is-invalid",
    validClass: "is-valid",
    errorElement: "div",
    onfocusout: function(elem) { this.element(elem); },
    errorPlacement: function(error, element) {
      error.addClass("invalid-feedback");
      element.after(error);
    },
    rules: {
      username: {
        required: true,
        minlength: 6,
        maxlength: 20,
        pattern: /^[A-Za-z0-9]+$/
      },
      password: {
        required: true,
        minlength: 6
      },
      confirm_password: {
        required: true,
        minlength: 6,
        equalTo: "#password"
      }
    },
    messages: {
      username: {
        required: "請輸入用戶名",
        minlength: "至少 6 個字元",
        maxlength: "最多 20 個字元",
        pattern: "只能使用英數字"
      },
      password: {
        required: "請輸入密碼",
        minlength: "密碼至少需 6 個字元"
      },
      confirm_password: {
        required: "請確認密碼",
        minlength: "密碼至少需 6 個字元",
        equalTo: "兩次密碼輸入不一致"
      }
    },
    submitHandler: function(form) {
      form.submit();
    }
  });
});