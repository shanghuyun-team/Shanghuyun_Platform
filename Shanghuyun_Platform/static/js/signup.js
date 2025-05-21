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
      password1: {
        required: true,
        minlength: 8,
        pwcheck: true,
        notEqualToUsername: true
      },
      password2: {
        required: true,
        minlength: 6,
        equalTo: "#id_password1"
      }
    },
    messages: {
      username: {
        required: "請輸入用戶名稱",
        minlength: "至少 6 個字元",
        maxlength: "最多 20 個字元",
        pattern: "只能使用英數字"
      },
      password1: {
        required: "請輸入密碼",
        minlength: "密碼至少需 8 個字元",
        pwcheck: "密碼需包含英文字母與數字，且不可全為數字",
        notEqualToUsername: "密碼不可與用戶名相同"
      },
      password2: {
        required: "請確認密碼",
        minlength: "密碼至少需 6 個字元",
        equalTo: "兩次密碼輸入不一致"
      }
    },
    invalidHandler: function(event, validator) {
      if (validator.errorList.length) {
        // 顯示第一個錯誤訊息（中文）
        $("#form-non-field-errors")
          .removeClass("d-none")
          .text(validator.errorList[0].message);
      } else {
        $("#form-non-field-errors").addClass("d-none").text("");
      }
    },
    success: function(label, element) {
      $("#form-non-field-errors").addClass("d-none").text("");
    },
    submitHandler: function(form, event) {
      event.preventDefault();
      var $form = $(form);
      var postData = $form.serialize();
      var csrftoken = $("input[name='csrfmiddlewaretoken']").val();
      $.ajax({
        url: $form.attr('action'),
        type: 'POST',
        data: postData,
        beforeSend: function(xhr) {
          xhr.setRequestHeader('X-CSRFToken', csrftoken);
        },
        success: function(data) {
          // 嘗試判斷是否有成功註冊
          if (data.success) {
            window.location.href = data.redirect_url || '/';
          } else if (data.error) {
            $("#form-non-field-errors").removeClass("d-none").text(data.error);
          } else {
            // 若回傳 HTML，嘗試解析 non_field_errors
            var html = $(data);
            var serverErrors = html.find('.nonfield, .errorlist.nonfield, .errorlist li').text();
            if (serverErrors) {
              $("#form-non-field-errors").removeClass("d-none").text(serverErrors);
            } else {
              window.location.reload();
            }
          }
        },
        error: function(xhr) {
          var msg = "註冊失敗，請檢查資料或稍後再試";
          if (xhr.responseText) {
            try {
              var resp = JSON.parse(xhr.responseText);
              if (resp.error) msg = resp.error;
            } catch (e) {}
          }
          $("#form-non-field-errors").removeClass("d-none").text(msg);
        }
      });
      return false;
    }
  });

  var serverErrors = $(".nonfield, .errorlist.nonfield, .errorlist li").text();
  if (serverErrors && serverErrors.length > 0) {
    $("#form-non-field-errors")
      .removeClass("d-none")
      .text(serverErrors);
  }

  // 自訂密碼驗證規則
  $.validator.addMethod("pwcheck", function(value, element) {
    return /[A-Za-z]/.test(value) && /[0-9]/.test(value) && !/^\d+$/.test(value);
  });
  $.validator.addMethod("notEqualToUsername", function(value, element) {
    var username = $("#id_username").val();
    return value !== username;
  });
});