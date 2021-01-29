
function validDropArea(e){
    return (' ' + e.target.className + ' ').indexOf(' my-dragdrop ') > -1;
}
function attachDropEvents(a) {
    a.ondragover = function (e) {
        if (validDropArea(e))
            e.preventDefault();
    };
    a.ondrop = function (e) {
        let url = window.location.href;
        let patientElId = e.dataTransfer.getData("Text");
        let patientEl = document.getElementById(patientElId);
        e.target.appendChild(patientEl);
        if (e.target.tagName === 'TD') {
            e.target.classList.remove('my-dragdrop');
            const obj = {
                patient_id: patientElId,
                reservation_id: patientEl.dataset.reservation_id,
                employee_id: e.target.dataset.employee_id,
                hour: e.target.dataset.hour,
                date: e.target.dataset.date
            };
            fetch(url, {
                    method: 'POST',
                    body: JSON.stringify(obj),
                })
                .then(async (response) => {
                    return await response.text();
                })
                .then(data => {
                    console.log(data);
                    e.target.firstElementChild.dataset.timetable_id = data;
                })
                .catch(e => console.error('Błąd' + e));

        }
        else if (e.target.tagName === 'DIV'){
            const obj = {
                timetable_id: patientEl.dataset.timetable_id
            };
            fetch(url, {
                    method: 'DELETE',
                    body: JSON.stringify(obj),
                })
                .then(async (response) => {
                    patientEl.dataset.timetable_id = "";
                })
                .catch(e => console.error('Błąd' + e));
        }
        e.preventDefault();
    };
}

document.addEventListener("DOMContentLoaded", function () {
    for (let i=0, patientEl, patientsEl = document.getElementsByClassName("my-patient"); patientEl = patientsEl[i]; i++){
        patientEl.draggable = true;
        patientEl.ondragstart = function(e){
            e.dataTransfer.setData("Text", e.target.id);
            if (e.target.parentElement.tagName === 'TD'){
                e.target.parentElement.classList.add('my-dragdrop');
                attachDropEvents(e.target.parentElement);
            }
        };
    }
    for (let i=0, place, places = document.getElementsByClassName("my-dragdrop"); place = places[i]; i++){
        attachDropEvents(place);
    }
});