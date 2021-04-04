PATIENT_DATA = (
    'Andrzej Adamczyk',
    'Adam Andruszkiewicz',
    'Waldemar Andzel',
    'Jan Ardanowski',
    'Iwona Arent',
    'Marek Ast',
    'Zbigniew Babalski',
    'Piotr Babinetz',
    'Ryszard Bartosik',
    'Barbara Bartuś',
    'Mieczysław Baszko',
    'Dariusz Bąk',
    'Jerzy Bielecki',
    'Mariusz Błaszczak',
    'Rafał Bochenek',
    'Joanna Borowiak',
    'Kamil Bortniczuk',
    'Bożena Borys-Szopa',
    'Waldemar Buda',
    'Stanisław Bukowiec',
    'Lidia Burzyńska',
    'Zbigniew Chmielowiec',
    'Kazimierz Choma',
    'Dominika Chorosińska',
    'Tadeusz Chrzan',
    'Anna Cicholska',
    'Michał Cieślak',
    'Krzysztof Czarnecki',
    'Przemysław Czarnecki',
    'Witold Czarnecki',
    'Przemysław Czarnek',
    'Arkadiusz Czartoryski',
    'Anita Czerwińska',
    'Katarzyna Czochara',
    'Anna Dąbrowska-Banaszek',
    'Leszek Dobrzyński',
    'Zbigniew Dolata',
    'Bartłomiej Dorywalski',
    'Przemysław Drabek'
)


def change_patient():
    list_patient = []
    for patient in PATIENT_DATA:
        list_patient.append(patient.split(' '))
    for i in range(len(PATIENT_DATA)-3):
        list_patient[i] = [list_patient[i][0], list_patient[i+3][1]]
        print(list_patient[i])
    return list_patient[:-3]
