// 取得 CSRF Token 的通用函式
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(function() {
  // Register FilePond plugins
  FilePond.registerPlugin(
    FilePondPluginImagePreview,
    FilePondPluginFileValidateType // Register File Validate Type plugin
  );

  // Get a reference to the file input element
  const inputElement = document.querySelector('input[type="file"]#avatar');

  // Create FilePond instance
  const pond = FilePond.create(inputElement, {
    labelIdle: '拖曳或點擊上傳頭像 (最大 3MB)',
    imagePreviewHeight: 140,
    imageCropAspectRatio: '1:1',
    imageResizeTargetWidth: 150,
    imageResizeTargetHeight: 150,
    stylePanelLayout: 'compact circle',
    styleLoadIndicatorPosition: 'center bottom',
    styleProgressIndicatorPosition: 'right bottom',
    styleButtonRemoveItemPosition:  'bottom center',
    styleButtonProcessItemPosition: 'right bottom',
    maxFileSize: '3MB', 
    labelMaxFileSizeExceeded: '檔案太大',
    labelMaxFileSize: '最大檔案大小為 {filesize}',
    acceptedFileTypes: ['image/*'], // Restrict to image files
    labelFileTypeNotAllowed: '檔案類型無效', // Message for invalid file type
    fileValidateTypeLabelExpectedTypes: '請選擇圖片檔案', // Expected file type message
  });

  // Phone verification simulation with cooldown
  let resendCooldown = 60; // seconds
  let resendInterval;
  let verifying = false;

  function startResendCooldown() {
    verifying = true;
    $('#verifyPhoneBtn').prop('disabled', true).html(`重新驗證 (${resendCooldown}s)`);
    $('#resendCodeBtn').hide(); // Hide resend button during cooldown
    resendInterval = setInterval(() => {
      resendCooldown--;
      $('#verifyPhoneBtn').html(`重新驗證 (${resendCooldown}s)`);
      if (resendCooldown <= 0) {
        clearInterval(resendInterval);
        $('#verifyPhoneBtn').prop('disabled', false).text('驗證');
        $('#resendCodeBtn').show(); // Show resend button after cooldown
        resendCooldown = 60; // Reset cooldown
        verifying = false;
      }
    }, 1000);
  }

  $('#verifyPhoneBtn').on('click', function() {
    const phone = $('#phone').val();
    const verificationMsg = $('#phone-verification-message');
    if (phone && !verifying) {
      // Simulate sending OTP
      verificationMsg.text('驗證碼已寄送至您的手機。').removeClass('text-danger').addClass('text-success');
      $('#otp-input-group').slideDown();
      startResendCooldown(); // Start cooldown immediately after clicking verify
      // Here you would typically call a backend API to send SMS
    } else if (verifying) {
        verificationMsg.text('請稍後，驗證程序正在進行中。').removeClass('text-danger').removeClass('text-success');
    }
     else {
      verificationMsg.text('請先輸入手機號碼。').removeClass('text-success').addClass('text-danger');
    }
  });

  $('#resendCodeBtn').on('click', function() {
    const verificationMsg = $('#phone-verification-message');
    verificationMsg.text('驗證碼已重新寄送。').removeClass('text-danger').addClass('text-success');
    startResendCooldown(); // Start cooldown on resend
    // Simulate resending OTP
  });


  // jQuery Validation for Profile Edit Form
  $("#profile-edit-form").validate({
    errorClass: "is-invalid",
    validClass: "is-valid",
    errorElement: "div",
    errorPlacement: function(error, element) {
      error.addClass("invalid-feedback");
      if (element.prop("type") === "file") {
        error.insertAfter(element.closest('.avatar-upload-container'));
      } else if (element.attr("id") === "phone") {
        element.closest(".input-group").after(error);
      }
      else {
        element.after(error);
      }
    },
    rules: {
      realname: "required",
      nickname: "required",
      email: {
        required: true,
        email: true
      },
      phone: {
        required: true
        // Add phone validation if intl-tel-input is used
      },
      avatar: {
        accept: "image/*" // Validate file type
      }
      // Add rules for OTP if needed
    },
    messages: {
      realname: "請填寫真實姓名",
      nickname: "請填寫暱稱",
      email: {
        required: "請輸入電子郵件",
        email: "請輸入正確的 Email 格式"
      },
      phone: {
        required: "請輸入電話號碼"
      },
      avatar: {
        accept: "請上傳圖片格式的檔案 (jpg, png, gif)"
      }
    },
    submitHandler: function(form) {
      // form.submit(); // Replace with AJAX or actual form submission
      Swal.fire({
        title: '成功!',
        text: '個人資料已儲存 (模擬)',
        icon: 'success',
        confirmButtonColor: 'var(--accent-color)'
      });
    }
  });

  // jQuery Validation for Change Password Form
  $("#change-password-form").validate({
    errorClass: "is-invalid",
    validClass: "is-valid",
    errorElement: "div",
    errorPlacement: function(error, element) {
      error.addClass("invalid-feedback");
      element.after(error);
    },
    rules: {
      current_password: "required",
      new_password: {
        required: true,
        minlength: 8
      },
      confirm_password: {
        required: true,
        minlength: 8,
        equalTo: "#new-password"
      }
    },
    messages: {
      current_password: "請輸入目前密碼",
      new_password: {
        required: "請輸入新密碼",
        minlength: "密碼長度至少8個字元"
      },
      confirm_password: {
        required: "請再次輸入新密碼",
        minlength: "密碼長度至少8個字元",
        equalTo: "兩次輸入的密碼不一致"
      }
    },
    submitHandler: function(form) {
      $.ajax({
        url: '/api/v1/account/password/change/',
        type: 'PUT', // 修正為 PUT
        data: JSON.stringify({
          old_password: $('#current-password').val(),
          new_password: $('#new-password').val()
        }),
        contentType: 'application/json',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(res) {
          Swal.fire({
            title: '成功!',
            text: '密碼已更新',
            icon: 'success',
            confirmButtonColor: 'var(--accent-color)'
          });
          form.reset();
        },
        error: function(xhr) {
          Swal.fire({
            title: '錯誤',
            text: xhr.responseJSON?.old_password?.[0] || xhr.responseJSON?.detail || '密碼更新失敗',
            icon: 'error',
            confirmButtonColor: 'var(--accent-color)'
          });
        }
      });
    }
  });

  // 新密碼長度提示動態變色，避免與驗證訊息重複
  const $newPassword = $('#new-password');
  const $passwordHint = $('#password-length-hint');
  function updatePasswordHint() {
    if ($newPassword.hasClass('is-invalid')) {
      $passwordHint.hide();
      return;
    }
    $passwordHint.show();
    const val = $newPassword.val();
    if (val.length === 0) {
      $passwordHint.css('color', 'black');
    } else if (val.length < 8) {
      $passwordHint.css('color', 'red');
    } else {
      $passwordHint.css('color', 'green');
    }
  }
  $newPassword.on('input', updatePasswordHint);
  $newPassword.on('blur change', updatePasswordHint);
  // 初始狀態
  updatePasswordHint();

  // 頁面載入時自動取得個人資料並填入表單
  $.ajax({
    url: '/api/v1/account/profile/',
    type: 'GET',
    success: function(data) {
      $('#realname').val(data.real_name || '');
      $('#nickname').val(data.nickname || '');
      $('#address').val(data.address || '');
      $('#phone').val(data.phone || '');
      // 若API有回傳email（預設Profile沒有，需後端補上）
      if (data.email) $('#email').val(data.email);
      // 頭像預覽
      if (data.portrait) {
        // 若 portrait 為相對路徑，補 /media/
        let portraitUrl = data.portrait.startsWith('http') ? data.portrait : ('/media/' + data.portrait.replace(/^\/+/, ''));
        pond.addFile(portraitUrl, { type: 'local' });
      }
    },
    error: function(xhr) {
      // 可選：顯示錯誤訊息
      console.warn('載入個人資料失敗', xhr);
    }
  });
});