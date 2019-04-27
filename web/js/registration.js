function sendName() {
    user_name = $('#user_name').val()
    fetch('/back/user/name', {method: 'GET'})
        .then(resp => {console.log('Name was successfully sent')})
        .catch(err => {console.error(err)})
}

function onRecordStart() {
    startRecording();
    $('#recordButton').hide();
    $('#stopButton').show();
}

function onVoiceObtained(blob) {
    var url = URL.createObjectURL(blob);
    au = $('#audio')
    au[0].controls = true
    au[0].src = url
    au.show()

    function sendWav() {
        fetch('/back/voice', {method: 'POST', body: blob})
    }
    btn = $('#send')
    btn.click(sendWav)
    btn.show()
}

function onRecordStop() {
    $('#recordButton').show();
    $('#stopButton').hide();
    stopRecording(onVoiceObtained);
}

function sendControlWords() {
    const word1 = $('#word1').val()
    const word2 = $('#word2').val()
    const word3 = $('#word3').val()
    const word4 = $('#word4').val()
    const word5 = $('#word5').val()
    const data = {word1, word2, word3, word4, word5}

    fetch('/back/user/name', {method: 'POST', body: JSON.stringify(data), headers: {'Content-Type': 'application/json'}})
        .then(resp => {console.log('Name was successfully sent')})
        .catch(err => {console.error(err)})
}