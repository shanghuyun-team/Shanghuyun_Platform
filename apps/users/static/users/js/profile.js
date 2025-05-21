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
      // form.submit(); // Replace with AJAX or actual form submission
      Swal.fire({
        title: '成功!',
        text: '密碼已更新 (模擬)',
        icon: 'success',
        confirmButtonColor: 'var(--accent-color)'
      });
      form.reset();
    }
  });

  // Activate tab from URL hash if present
  var hash = window.location.hash;
  if (hash) {
    $('.profile-sidebar .nav-link[href="' + hash + '"]').tab('show');
  }

  // Update hash on tab change
  $('.profile-sidebar .nav-link').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
  });

  // Account Deletion with SweetAlert2
  $('#deleteAccountBtn').on('click', function() {
    Swal.fire({
      title: '確認刪除帳號',
      text: "您確定要刪除您的帳號嗎？此操作無法復原。",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d',
      confirmButtonText: '是的，刪除',
      cancelButtonText: '取消'
    }).then((result) => {
      if (result.isConfirmed) {
        Swal.fire({
          title: '再次確認刪除帳號',
          text: "這真的是最後的機會了。一旦刪除，所有資料將永久消失。您確定要繼續嗎？",
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#dc3545',
          cancelButtonColor: '#6c757d',
          confirmButtonText: '是的，我非常確定',
          cancelButtonText: '取消'
        }).then((result2) => {
          if (result2.isConfirmed) {
            Swal.fire({
              title: '最終確認',
              html: `
                <p>為完成刪除程序，請在下方輸入框中輸入 "DELETE" (全大寫)。</p>
                <input type="text" id="swal-input-delete" class="swal2-input" placeholder="DELETE">
              `,
              icon: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#dc3545',
              cancelButtonColor: '#6c757d',
              confirmButtonText: '確認刪除',
              cancelButtonText: '取消',
              preConfirm: () => {
                const inputValue = document.getElementById('swal-input-delete').value;
                if (inputValue !== 'DELETE') {
                  Swal.showValidationMessage('輸入不正確。請輸入 "DELETE"');
                  return false;
                }
                return inputValue;
              }
            }).then((result3) => {
              if (result3.isConfirmed && result3.value === 'DELETE') {
                // Simulate account deletion
                Swal.fire(
                  '已刪除!',
                  '您的帳號已成功刪除 (模擬)。您將被登出。',
                  'success'
                ).then(() => {
                  // Here you would typically redirect to a logout page or homepage
                  // window.location.href = "/logout";
                  console.log("Account deletion process completed.");
                });
              }
            });
          }
        });
      }
    });
  });

});