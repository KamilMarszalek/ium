# Projekt IUM – Etap 1 (wersja wstępna)  
## Zadanie 7 – Kryteria długich noclegów

Autorzy: Damian D'Souza, Kamil Marszałek

---

## 1. Cel projektu z perspektywy Nocarz

W ramach projektu wcielamy się w rolę analityków pracujących dla portalu **Nocarz**. Naszym zadaniem jest odpowiedź na zgłoszoną potrzebę:

> „Nie do końca rozumiemy jakimi kryteriami kierują się klienci, którzy rezerwują dłuższe noclegi. Taka informacja bardzo pomogłaby naszym konsultantom.”

Celem projektu jest więc zrozumienie, co wyróżnia rezerwacje długich pobytów – zarówno po stronie klientów, jak i ofert oraz kontekstu (czas, sezon, cena). Efektem prac ma być zestaw konkretnych wniosków i narzędzi, które pozwolą konsultantom:

- lepiej doradzać klientom planującym dłuższe wyjazdy,
- szybciej identyfikować oferty atrakcyjne dla długich pobytów,
- lepiej rozumieć, jakie „profile” klientów skłonne są rezerwować dłużej.

---

## 2. Wstępna definicja problemu

Żeby móc przejść do analiz, potrzebujemy uzgodnić kilka kwestii.

**Co uznajemy za „długi pobyt”**

Na razie zakładamy, że:

- długość pobytu będziemy liczyć jako liczbę nocy między datą zameldowania a datą wymeldowania,
- „długi pobyt” zostanie zdefiniowany jako pobyt trwający co najmniej X nocy (np. 7, 14, 30 – do ustalenia).

---

## 3. Nasza propozycja podejścia

### 3.1. Część analityczna (opisowa)

Po otrzymaniu danych planujemy:

- przygotować podstawowe statystyki długości pobytów (rozkłady, typowe wartości),
- sprawdzić, jak długość pobytu zależy od:
  - regionu i typu lokalu,
  - pory roku i dnia tygodnia,
  - poziomu cen,
  - historii klienta,
- porównać zachowania klientów rezerwujących krótko vs długo (np. jak długo szukają, ile ofert przeglądają, z jakich filtrów korzystają – jeśli takie dane będą dostępne).

Efektem tej części będzie zestaw wniosków i wykresów.

### 3.2. Część modelowa (predykcyjna)

Równolegle chcemy zbudować prosty model, który:

- albo przewiduje **przybliżoną długość pobytu** (w dniach),
- albo szacuje **prawdopodobieństwo długiego pobytu** (według wspólnie ustalonej definicji).

Najważniejsze z naszej perspektywy jest to, aby model pozwalał odpowiedzieć na pytanie:

> „Co w przypadku tego konkretnego klienta/oferty najbardziej przemawia za dłuższym pobytem?”

Dlatego planujemy użyć technik, które pozwalają wskazać **najważniejsze czynniki** wpływające na decyzję o dłuższym pobycie i przedstawić je w przystępnej formie (np. ranking cech, krótkie „historie” przypadków).

---

## 5. Jakich danych potrzebujemy?

Na tym etapie nie mamy jeszcze dostępu do danych, ale na podstawie opisu systemu Nocarz szacujemy, że dla realizacji projektu kluczowe (o ile są dostępne) będą następujące kategorie danych:

1. **Dane o rezerwacjach**  
   - daty: rezerwacji, przyjazdu (check-in), wyjazdu (check-out),
   - liczba gości,
   - cena całkowita i/lub cena za noc,
   - status rezerwacji (potwierdzona, anulowana, zakończona).

2. **Dane o lokalach**  
   - lokalizacja (miasto, region),
   - typ lokalu (pokój, apartament, dom itp.),
   - podstawowe parametry (liczba pokoi, łóżek, powierzchnia),
   - dostępne udogodnienia (np. kuchnia, WiFi, parking),
   - informacje o opiniach (średnia ocena, liczba recenzji).

3. **Dane o klientach**  
   - kraj pochodzenia,
   - liczba wcześniejszych rezerwacji,
   - ewentualnie: średnia długość pobytu w historii, średnia wartość rezerwacji.

4. **Dane o sesjach w serwisie**  
   - długość sesji,
   - liczba przeglądanych ofert,
   - użyte filtry (cena, lokalizacja, udogodnienia),
   - urządzenie (desktop / mobile),

Po otrzymaniu informacji od Państwa dostosujemy listę do faktycznie dostępnych tabel i pól.

---

## 6. Co chcemy Państwu dostarczyć na koniec projektu?

W efekcie prac (po etapach 1 i 2) planujemy przygotować:

1. **Raport z wnioskami biznesowymi**, w którym:
   - opiszemy, jakie profile klientów i ofert sprzyjają długim pobytom,
   - wskażemy najważniejsze czynniki (np. cena, sezon, typ lokalu, historia klienta),
   - zaproponujemy kilka prostych reguł/obserwacji, które konsultanci mogą wykorzystać w rozmowach z klientami.

2. **Prosty model predykcyjny** (udostępniony w formie mikroserwisu), który:
   - na podstawie danych o planowanej rezerwacji oszacuje długość pobytu lub prawdopodobieństwo długiego pobytu,
   - zwróci także informację, które cechy w danym przypadku miały największy wpływ na wynik.

3. **Materiał techniczny**  
   - opis wykorzystanych metod,
   - sposób trenowania modeli,
   - przykładowe wywołania API mikroserwisu.

---

## 7. Otwarte kwestie do uzgodnienia z Państwem

Na chwilę obecną kluczowe kwestie, które chcielibyśmy doprecyzować, to:

1. **Dokładna definicja „długiego pobytu”** (liczba nocy i ewentualne rozróżnienie na różne kategorie).
2. **Zakres okresu historycznego**, który powinniśmy analizować.
3. **Jakie dane są faktycznie dostępne** w systemie Nocarz (czy możemy liczyć na wszystkie wymienione kategorie, czy są jakieś ograniczenia).
4. **Priorytet**: czy w większym stopniu zależy Państwu na:
   - wyjaśnianiu i wizualizacji zjawiska,
   - czy na gotowym modelu przewidującym, jak długo klient może zostać.

Po uzyskaniu odpowiedzi zaktualizujemy ten dokument, doprecyzujemy założenia oraz przejdziemy do właściwej analizy danych.
