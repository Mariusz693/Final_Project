![Coders-Lab-1920px-no-background](https://user-images.githubusercontent.com/152855/73064373-5ed69780-3ea1-11ea-8a71-3d370a5e7dd8.png)


## Projekt końcowy.

Aplikacja obsługująca ośrodek rehabilitacyjny

Główne założenia projektu:
* Stworzenie modelu użytkownika z podziałem na administratora ośrodka, rehabilitantów i klienta ośrodka
* Stworzenie modelu pokoju
* Stworzenie modelu rezrwacji, z relacją do modelu pokoju, klienta ośrodka, z datą rozpoczęcia i zakończenia pobytu. ewentualną notatką
* Stworzenie modelu grafiku, dla osób aktualnie obecnych, z relacjami do pracownika, klienta, rezerwacji, z datą dnia i godziną ćwiczeń
* Strona główna, z opcją logowania
* Po zalogowaniu się jako administrator ośrodka z podstrony uzyskuje dostęp do bazy danych klientów ośrodka i rehabilitantów, ich dodawaniem do bazy, usuwaniem
* Podstrony z terminarzem, odwzorującej model rezerwacji skąd można dodawać lub usuwać rezerwacje dla danych klientów, strona wyświetla rezerwacje dla pojedyńczego miesiąca i kolejnych pokoi
* Podstrona z grafikiem dziennym, w której dla danego dnia pobierani są kliencji aktualnie przebywający na turnusie, oraz pracownicy. Dla każdego pacjenta można przyporządkować mu rehebilitanta i godzinę zajęć
* Klient ośrodka po mailowym otrzymaniu linku aktywacyjnego z tokenem, ustawieniu hasła, logując się na swoje konto, ma dostęp do edycji swoich danych, sprawdzenia zarezerwowanych terminów pobytu oraz będąc na turnusie do codziennego grafiku zajęć, bez możliwości edycji rezerwacji i grafiku
* Pracownik ośrodka po mailowym otrzymaniu linku aktywacyjnego z tokenem, ustawieniu hasła, logując się na swoje konto, ma dostęp do edycji swoich danych oraz do codziennego grafiku zajęć, bez możliwości edycji grafiku
