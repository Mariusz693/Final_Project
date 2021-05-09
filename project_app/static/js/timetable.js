
function attachDropEvents(a) {
    a.ondragover = function (e) {
        e.preventDefault();
    };
    a.ondrop = function (e) {
        let url = window.location.href;
        let patientElId = e.dataTransfer.getData('patient_id');
        let patientEl = document.getElementById(patientElId);
        let timetableId = patientEl.dataset.timetable_id;
        e.target.appendChild(patientEl);
        if (e.target.tagName === 'TD' && timetableId) {
            e.target.classList.remove('my-dragdrop');
            const obj = {
                timetable: timetableId,
                employee: e.target.dataset.employee_id,
                hour_timetable: e.target.dataset.hour
            };
            fetch(url, {
                method: 'PUT',
                body: JSON.stringify(obj),
            })
            .then(response => {
                if (response.status !== 200){
                    throw Error();
                }
            })
            .catch(error => {
                window.location = url;
            });
        }
        else if (e.target.tagName === 'TD') {
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
            .then(response => {
                if (response.status === 200){
                    return response.json();
                }
                else {
                    throw Error();
                }
            })
            .then(data => {
                e.target.firstElementChild.dataset.timetable_id = data['instance'];
            })
            .catch(error => {
                window.location = url;
            });
        }
        else if (e.target.id === 'free-patient'){
            const obj = {
                timetable: patientEl.dataset.timetable_id
            };
            fetch(url, {
                method: 'DELETE',
                body: JSON.stringify(obj),
            })
            .then(response => {
                if (response.status === 200){
                    patientEl.dataset.timetable_id = "";
                }
                else {
                    throw Error();
                }
            })
            .catch(error => {
                window.location = url;
            });
        } else {
            window.location = url;
        }
        e.preventDefault();
    };
}

document.addEventListener("DOMContentLoaded", function () {
    for (let i=0, patientEl, patientsEl = document.getElementsByClassName('my-timetable-patient-element'); patientEl = patientsEl[i]; i++){
        patientEl.draggable = true;
        patientEl.ondragstart = function(e){
            e.dataTransfer.setData('patient_id', e.target.id);
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