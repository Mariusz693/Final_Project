![Coders-Lab-1920px-no-background](https://user-images.githubusercontent.com/152855/73064373-5ed69780-3ea1-11ea-8a71-3d370a5e7dd8.png)


## Projekt końcowy.

Aplikacja obsługująca ośrodek rehabilitacyjny

Główne założenia projektu:
* Stworzenie modelu użytkownika z podziałem na administratora ośrodka, rehabilitantów i klienta ośrodka
* Stworzenie modelu pokoju
* Stworzenie modelu rezrwacji, z relacją do modelu pokoju, klienta ośrodka, z datą rozpoczęcia i zakończenia pobytu. ewentualną notatką
* Stworzenie modelu grafiku, dla osób aktualnie obecnych, z relacjami do pracownika, klienta, rezerwacji, z datą dnia i godziną ćwiczeń
* Strona główna, z opcją logowania
* Po zalogowaniu się jako administrator ośrodka z podstrony uzyskuje dostęp do bazy danych klientów ośrodka i rehabilitantów, ich dodawaniem do bazy, edycją, usuwaniem
* Podstrony z terminarzem, odwzorującej model rezerwacji skąd można dodawać lub usuwać rezerwacje dla danych klientów, strona wyświetla rezerwacje dla pojedyńczego miesiąca i kolejnych pokoji
* Podstrona z grafikiem dziennym, w której dla danego dnia pobierani są kliencji aktualnie przebywający na turnusie, oraz pracownicy. Dla każdego pacjenta można przyporządkować mu rehebilitanta i godzinę zajęć
* Klient ośrodka logując się na swoje konto, po mailowym otrzymaniu loginu i hasła, ma dostęp do edycji swoich danych, sprawdzenia zarezerwowanych terminów pobytu oraz będąc na turnusie do codziennego grafiku zajęć, bez możliwości edycji rezerwacji i grafiku
* Pracownik ośrodka logując się na swoje konto, po mailowym otrzymaniu loginu i hasła, ma dostęp do edycji swoich danych oraz do codziennego grafiku zajęć, bez możliwości edycji grafiku



Wymagania:
* Projekt musi być aplikacją napisaną w Django
* Projekt musi posiadać co najmniej 5 modeli
* Projekt musi korzystać z bazy danych PostgreSQL
* W bazie danych powinny znajdować się co najmniej 3 tabele i dwie relacje (tabele tworzone automatycznie przez Django się w to nie wliczają).
* W projekcie są użyte relacje 1:wiele i wiele:wiele
* W aplikacji powinno znajdować się conajmniej 5 widoków (obsługiwanych przez różne adresy URL).
* W aplikacji musi znajdować się co najmniej jeden widok dostepny tylko la zalogowanego użytkownika (można używać Django auth system)
* Aplikacja powinna mieć co najmniej jeden formularz (obsługiwany metodą POST).
* W aplikacji powinny znaleźć się conajmniej 3 testy napisane przy użyciu frameworka pytest, pokrywające kluczowe funkcjonalności aplikacji. Do każdego widoku powinny być co najmniej dwa testy.
* Każda klasa i funkcja powinna posiadać przynajmniej jednolinijkową dokumentację.
