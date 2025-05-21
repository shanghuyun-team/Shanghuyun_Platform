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
        }
    },
    messages: {
        username: {
        required: "請輸入用戶名稱",
        minlength: "至少 6 個字元",
        maxlength: "最多 20 個字元",
        pattern: "只能使用英數字"
        }
    },
    invalidHandler: function(event, validator) {
        if (validator.errorList.length) {
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
            if (data.success) {
            window.location.href = data.redirect_url || '/';
            } else {
            // 嘗試解析伺服器回傳的 HTML 錯誤
            var html = $(data);
            var serverErrors = html.find('.nonfield, .errorlist.nonfield, .errorlist li').text();
            if (serverErrors && serverErrors.indexOf('已被占用') !== -1) {
                $("#form-non-field-errors").removeClass("d-none").text("用戶名稱已被使用");
            } else if (serverErrors) {
                $("#form-non-field-errors").removeClass("d-none").text(serverErrors);
            } else {
                window.location.reload();
            }
            }
        },
        error: function(xhr) {
            $("#form-non-field-errors").removeClass("d-none").text("註冊失敗，用戶名稱已被使用");
        }
        });
        return false;
    }
    });
});