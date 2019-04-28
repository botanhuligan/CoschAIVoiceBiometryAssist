function hashSystemCode() {
    const systemCode = $('#system_code').val()
    $('#system_code').val(CryptoJS.SHA256(systemCode))
}