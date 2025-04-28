function showNotification(from, align, message, type="success") {
    $.notify({
      icon: "tim-icons icon-bell-55",
      message: message
    }, {
      type: type,
      timer: 8000,
      placement: {
        from: from,
        align: align
      }
    });
  }