# Analiza danych

## Dostępne atrybuty
W tej sekcji omówimy różne atrybuty dostępne w naszym zestawie danych oraz ich znaczenie.

### Dane listings.csv
W pliku `listings.csv` znajduje się 79 atrybutów między innymi:
- `id`: Unikalny identyfikator oferty.
- `name`: Nazwa oferty.
- `price`: Cena oferty.
- `room_type`: Typ pokoju (np. całe mieszkanie, prywatny pokój).
- `amenities`: Lista udogodnień dostępnych w ofercie np. czy jest pralka.

### Dane reviews.csv
W pliku `reviews.csv` znajduje się 6 atrybutów:
- `listing_id`: Unikalny identyfikator oferty, do której odnosi się recenzja.
- `id`: Unikalny identyfikator recenzji.
- `date`: Data dodania recenzji.
- `reviewer_id`: Unikalny identyfikator recenzenta.
- `reviewer_name`: Imię recenzenta.
- `comments`: Treść recenzji.

### Dane session.csv
W pliku `session.csv` znajduje się 7 atrybutów:
- `action`: Typ akcji wykonanej przez użytkownika (np. wyszukiwanie, obejrzenie oferty, rezerwacja oferty).
- `user_id`: Identyfikator użytkownika wykonującego akcję.
- `timestamp`: Znacznik czasu wykonania akcji.
- `listing_id`: Identyfikator oferty, na której wykonano.
- `booking_date`: Data rezerwacji oferty.
- `booking_duration`: (Prawdopodobnie) data zakończenia rezerwacji, chociaż nazwa sugeruje że to powinna być liczba!.
- `booking_id`: Identyfikator rezerwacji oferty.

### Dane users.csv
W pliku `users.csv` znajduje się 7 atrybutów:
- `id`: Identyfikator użytkownika.
- `name`: Imię użytkownika.
- `surname`: Nazwisko użytkownika.
- Dane adresowe (prawdopodobnie adres zamieszkania użytkownika):
  - `city`: Miasto.
  - `street`: Ulica.
  - `street_number`: Numer domu.
  - `postal_code`: Kod pocztowy.