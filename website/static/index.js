function deleteNote(noteid) {
    fetch('/deleteNote', {
        method: 'POST',
        body: JSON.stringify({noteid: noteid})
    }).then((_res) => {
        window.location.href = "/";
    })
}