
function attachDropEvents(a) {
    a.ondragover = function (e) {
        e.preventDefault();
    };
    a.ondrop = function (e) {
        let url = window.location.href;
        let patientElId = e.dataTransfer.getData('Text');
        let patientEl = document.getElementById(patientElId);
        e.target.appendChild(patientEl);
        if (e.target.tagName === 'TD') {
            e.target.classList.remove('my-dragdrop');
            const obj = {
                patient: patientElId,
                reservation: patientEl.dataset.reservation_id,
                employee: e.target.dataset.employee_id,
                hour_timetable: e.target.dataset.hour,
                day_timetable: e.target.dataset.date
            };
            fetch(url, {
                    method: 'POST',
                    body: JSON.stringify(obj),
                })
                .then(async (response) => {
                    return await response.text();
                })
                .then(data => {
                    if (data) {
                        e.target.firstElementChild.dataset.timetable_id = data;
                    }
                    else {
                        window.location = url;
                    }
                })
                .catch(e => console.error('Błąd' + e));

        }
        else if (e.target.tagName === 'DIV'){
            const obj = {
                timetable: patientEl.dataset.timetable_id
            };
            fetch(url, {
                    method: 'DELETE',
                    body: JSON.stringify(obj),
                })
                .then(async (response) => {
                    return await response.text();
                })
                .then(data => {
                    if (data) {
                        patientEl.dataset.timetable_id = "";
                    }
                    else {
                        window.location = url;
                    }
                })
                .catch(e => console.error('Błąd' + e));
        }
        e.preventDefault();
    };
}

document.addEventListener("DOMContentLoaded", function () {
    for (let i=0, patientEl, patientsEl = document.getElementsByClassName('my-timetable-patient-element'); patientEl = patientsEl[i]; i++){
        patientEl.draggable = true;
        patientEl.ondragstart = function(e){
            e.dataTransfer.setData('Text', e.target.id);
            if (e.target.parentElement.tagName === 'TD'){
                e.target.parentElement.classList.add('my-dragdrop');
                attachDropEvents(e.target.parentElement);
            }
        };
    }
    for (let i=0, place, places = document.getElementsByClassName('my-dragdrop'); place = places[i]; i++){
        attachDropEvents(place);
    }
});