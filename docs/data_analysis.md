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
- tekstowe pola opisowe np. `description`, `neighborhood_overview`.

### Dane reviews.csv
W pliku `reviews.csv` znajduje się 6 atrybutów:
- `listing_id`: Unikalny identyfikator oferty, do której odnosi się recenzja.
- `id`: Unikalny identyfikator recenzji.
- `date`: Data dodania recenzji.
- `reviewer_id`: Unikalny identyfikator recenzenta.
- `reviewer_name`: Imię recenzenta.
- `comments`: Treść recenzji.

### Dane sessions.csv
W pliku `sessions.csv` znajduje się 7 atrybutów:
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

## Co jest istotne dla naszego problemu?
Chcemy dowiedzieć się, na podstawie jakich czynników użytkownicy rezerwują długie pobyty. Do zamodelowania problemu niezbędne będą dane występujące w pliku `sessions.csv`, gdyż to właśnie stamtąd możemy uzyskać informacje o długości rezerwacji. Data rozpoczęcia pobytu i data zakończenia pobytu (lub czas trwania rezerwacji - być może jest błąd w kolumnie) są kluczowymi atrybutami do analizy. Stworzymy na ich podstawie pojęcie binarne - `long_stay` - i właśnie to chcemy, żeby model przewidywał jak najlepiej po wytrenowaniu. Z kolei z pliku `listings.csv` możemy pozyskać informacje o cechach ofert, które mogą wpływać na decyzje użytkowników dotyczące długości pobytu, takie jak cena, typ pokoju czy dostępne udogodnienia.  Plik `users.csv` może dostarczyć dodatkowych informacji demograficznych o użytkownikach, które również mogą mieć wpływ na ich wybory rezerwacyjne. Plik `reviews.csv` może być mniej istotny dla naszego konkretnego problemu, ale może dostarczyć dodatkowych informacji o jakości ofert i doświadczeniach użytkowników. 

Atrybuty w pliku `listings.csv` można podzielić zgrubsza na kilka kategorii:
- Ekonomia pobytu: 
    - `price`: Cena prawdopodobnie za noc. Jest ona podana z walutą (np. "$100.00"). Należałoby ją przekształcić na wartość numeryczną.
    - `minimum_nights`: Minimalna liczba nocy, na jaką można dokonać rezerwacji. Niektóre lokale są dostępne np. tylko na dłuższe pobyty (>30 dni).
    - `maximum_nights`: Maksymalna liczba nocy, na jaką można dokonać rezerwacji. Niektóre obiekty mogą zezwalać tylko na krótkie pobyty np. ich maksymalna liczba nocy to 7.
    - `has_availability`: Czy lokal jest dostępny do rezerwacji.
- Standard i udogodnienia:
    - `room_type`: Czy to całe mieszkanie, czy pokój prywatny lub współdzielony. Przy długich pobytach potencjalnie większa przestrzeń i prywatność mogą być ważne.
    - `amenities`: Zawiera listę udogodnień oferowanych przez lokal, takich jak pralka, kuchnia, Wi-Fi, akceptowanie zwierząt itp. Udogodnienia te mogą znacząco wpłynąć na komfort długiego pobytu.
    - `accommodates`: Liczba osób, które lokal może pomieścić. Dla dłuższych pobytów może być istotne, czy lokal jest odpowiedni dla większych grup lub rodzin.
    - `bedrooms`, `beds`: Liczba sypialni i łóżek w lokalu. Więcej sypialni i łóżek może być korzystne dla dłuższych pobytów, zwłaszcza dla rodzin lub grup.
    - `bathrooms`: Liczba łazienek w lokalu. Więcej łazienek może zwiększyć komfort podczas dłuższych pobytów.
    - `bathrooms_text`: Opis łazienek - czy są wspólne, prywatne
- Lokalizacja i otoczenie:
    - `neighbourhood_cleansed`: Nazwa dzielnicy, w której znajduje się lokal.
    - `neighbourhood_overview`: Opis okolicy. Dla długich pobytów ważne może być, czy okolica jest spokojna, bezpieczna i czy oferuje udogodnienia takie jak sklepy, restauracje itp. W przeciwieństwie do krótkich pobytów, gdzie lokalizacja w centrum miasta, blisko miejsc turystycznie atrakcyjnych może być bardziej pożądana, długie pobyty mogą wymagać bardziej zrównoważonej lokalizacji.
    - `latitude`, `longitude`: Dokładne współrzędne geograficzne lokalu. Mogą być użyteczne do analizy lokalizacji i jej wpływu na decyzje rezerwacyjne.
- Zaufanie i wiarygodność:
    - `host_is_superhost`: Czy gospodarz ma status superhosta. Gospodarze z tym statusem mogą być postrzegani jako bardziej wiarygodni, co może wpływać na decyzje dotyczące długich pobytów.
    - `host_response_time`: Czas odpowiedzi gospodarza. Szybka odpowiedź może być ważna dla gości planujących dłuższe pobyty. Lepiej, gdy gospodarz szybko odpowiada na zapytania np. within an hour.
    - `review_scores_rating`: Ogólna ocena lokalu.
    - `review_scores_value`: Ocena stosunku jakości do ceny.
    - `number_of_reviews`: Liczba recenzji. Większa liczba recenzji może świadczyć o popularności i zaufaniu do lokalu.

Z pliku `users.csv` nie użyjemy danych personalnych takich jak imię, nazwisko czy ulica. Być może użyjemy atrybut `city`, aby zobaczyć, czy lokalizacja użytkownika ma wpływ na długość rezerwacji np. czy osoby z większych miast rezerwują dłuższe pobyty.

Dane, które są w pliku `reviews.csv` prawdopodobnie nie będą użyte w naszym modelu, ponieważ recenzje są dodawane po zakończeniu pobytu i nie wpływają na decyzję o długości rezerwacji.
Ważniejsza może być zagregowana ocena, które jest już w pliku `listings.csv`.

## Problemy ze złączeniami danych między plikami

Aby wykorzystać dane z różnych plików, musimy je łączyć po kluczach. 
### Złączenie `sessions.csv` ↔ `listings.csv` 
Dla `listings.csv` i `sessions.csv` kluczami są odpowiednio `listings.id` oraz `sessions.listing_id`. Analizę pokrycia wykonujemy w dwóch ujęciach: pokrycie wierszy po złączeniu oraz pokrycie unikalnych kluczy (różnorodności ofert).

- Bez filtrowania po `action`: ok. 74% rekordów `sessions.csv` ma niepusty `listing_id`, a spośród nich ok. 67.6% znajduje dopasowanie w `listings.csv` (łączny row coverage ~50.1%). Jednocześnie tylko ok. 13.2% unikalnych `listing_id` obserwowanych w `sessions.csv` występuje w `listings.csv`, co sugeruje, że `listings.csv` jest ograniczonym podzbiorem ofert, a dopasowania dotyczą głównie najczęściej występujących listingów.

- Dla akcji `book_listing` (rezerwacje): ok. 80% rekordów ma niepusty `listing_id`, jednak tylko ok. 7.7% z nich znajduje dopasowanie w `listings.csv` (łączny row coverage ~6.2%). Oznacza to, że cechy ofert z `listings.csv` będą dostępne tylko dla niewielkiej części rezerwacji; trening modelu oparty głównie o cechy ofert może być przez to niemożliwy lub silnie obciążony selekcją danych.

Jednak zauważyliśmy, że wiele brakujących `id` w `listings.csv` można by było odzyskać, analizując kolumnę `listing_url` i wyciągając z niej identyfikatory ofert. Po naprawie braków w `listings.csv`, ponowiliśmy analizę złączeń:
- Bez filtrowania po `action`: pokrycie wierszy po złączeniu wzrosło do ok. 60.3%, a pokrycie unikalnych kluczy do ok. 15.8%. Natomiast dopasowanie wzrosło do ok. 81.4% rekordów z niepustym `listing_id`.
- Dla akcji `book_listing`: pokrycie wierszy po złączeniu wzrosło do ok. 7.4%, a pokrycie unikalnych kluczy do ok. 9.4%. Dopasowanie wzrosło do ok. 9.3% rekordów z niepustym `listing_id`. Mimo poprawy, cechy ofert z `listings` nadal będą dostępne tylko dla małej części rezerwacji, więc będzie problem z trenowaniem.

### Złączenie `sessions.csv` ↔ `users.csv`
Klucz łączący to `sessions.user_id` oraz `users.id`.

- Bez filtrowania po `action`: ok. 80% rekordów `sessions.csv` ma niepusty `user_id`, a spośród nich ok. 80% znajduje dopasowanie w `users.csv` (łączny row coverage ~64%). Pokrycie unikalnych `user_id` wynosi ok. 80%, co sugeruje, że dla większości użytkowników obecnych w sesjach istnieją odpowiadające im dane w `users.csv`, choć ok. 20% identyfikatorów nie jest możliwe do sparowania.

- Dla akcji `book_listing` (rezerwacje): wyniki są bardzo zbliżone.

### Złączenie `reviews.csv` ↔ `users.csv`
Klucz łączący to `reviews.reviewer_id` oraz `users.id`.

- Ok. 80% rekordów `reviews.csv` ma niepusty `reviewer_id`, a spośród nich ok. 80% znajduje dopasowanie w `users.csv` (łączny row coverage ~64%). Pokrycie unikalnych `reviewer_id` wynosi ok. 80%.

### Złączenie `reviews.csv` ↔ `listings.csv`
Klucz łączący to `reviews.listing_id` oraz `listings.id`.

- Ok. 80.1% rekordów w `reviews.csv` ma niepusty `listing_id`. Jednak tylko ok. 7.6% z nich znajduje dopasowanie w `listings.csv`, co daje łączne pokrycie wierszy po złączeniu na poziomie ok. 6.1%. Pokrycie po unikalnych kluczach jest również niskie: tylko ok. 8.0% unikalnych `listing_id` z `reviews.csv` występuje w `listings.csv` (`unique_key_coverage` ~0.0803). Wskazuje to, że `listings.csv` jest ograniczonym podzbiorem ofert i nie pozwala na wzbogacenie większości recenzji o cechy oferty.



## Braki danych
Przeanalizowaliśmy braki danych w plikach. Braki są dosyć duże:
- Plik `listings.csv` ma braki we wszystkich kolumnach - minimum 18% w kolumnie `host_has_profile_pic`, maksimum 100% w kolumnie `calendar_updated`. Jednak dla większości kolumn braki są w przedziale od ok. 20% do 40%.
- Plik `sessions.csv` również ma braki we wszystkich kolumnach minimum ok. 20% w kolumnach `action`, `user_id`, `timestamp`,
maksymalne braki to ok. 94% w kolumnach `booking_date`, `booking_duration`, `booking_id`. Braki w kolumnach związanych z rezerwacjami są zrozumiałe, ponieważ nie każda sesja kończy się rezerwacją. Jednak zmienną celową `long_stay` można będzie utworzyć tylko dla około 4% rekordów, gdyż braki w kolumnach `booking_date` i `booking_duration` nie występują jednocześnie.
- Pliki `users.csv` i `reviews.csv` mają braki we wszystkich kolumnach - minimum na poziomie około 20%.

