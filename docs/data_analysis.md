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
- liczne opisy

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

## Braki danych
Przeanalizowaliśmy braki danych w plikach. Braki są dosyć duże:
- Plik `listings.csv` ma braki we wszystkich kolumnach - minimum 18% w kolumnie `host_has_profile_pic`, maksimum 100% w kolumnie `calendar_updated`. Jednak dla większości kolumn braki są w przedziale od ok. 20% do 40%.
- Plik `sessions.csv` również ma braki we wszystkich kolumnach minimum ok. 20% w kolumnach `action`, `user_id`, `timestamp,
maksymalne braki to ok. 94% w kolumnach `booking_date`, `booking_duration`, `booking_id`. Braki w kolumnach związanych z rezerwacjami są zrozumiałe, ponieważ nie każda sesja kończy się rezerwacją. Jednak zmienną celową `long_stay` można będzie utworzyć tylko dla około 4% rekordów, gdyż braki w kolumnach `booking_date` i `booking_duration` nie występują jednocześnie.
- Pliki `users.csv` i `reviews.csv` mają braki we wszystkich kolumnach - minimum na poziomie około 20%.


