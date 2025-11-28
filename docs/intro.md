---
title: "Dokumentacja wstępna: Analiza długich rezerwacji (zadanie 7)"
author:
  - "Damian D'Souza"
  - "Kamil Marszałek"
date: "2025-11-27"
---

## 1. Definicja problemu

Obecnie brakuje nam wiedzy o czynnikach, które wpływają na długość rezerwacji. Nie wiemy, dlaczego niektórzy klienci rezerwują noclegi na dłuższe okresy (np. 7 dni+).

To utrudnia pracę konsultantom - nie mogą skutecznie doradzać właścicielom, jakie udogodnienia warto dodać, żeby przyciągnąć klientów szukających dłuższych pobytów.

**Cel projektu:** Zidentyfikować kluczowe czynniki (cechy oferty i profilu klienta), które zwiększają prawdopodobieństwo długiej rezerwacji. Dzięki temu konsultanci będą mogli konkretnie wskazać oferentom, co zmienić w ofercie (np. dodać szybkie Wi-Fi, wprowadzić rabaty tygodniowe), żeby zwiększyć szansę na dłuższe rezerwacje.

## 2. Podejście modelowe

### 2.1 Co modelujemy

- Zmienna wyjściowa *y*: 
  - `1` – rezerwacja „Długa”,  
  - `0` – rezerwacja „Krótka”.
- Robocza definicja długiej rezerwacji: pobyt np. powyżej 7 dni
- Wymaga potwierdzenia: Czy próg 7 dni jest odpowiedni?

- Rodzaj zadania: klasyfikacja binarna.


### 2.2 Wybór modelu
Potrzebujemy modelu interpretowalnego, który pozwoli zrozumieć, które cechy są najważniejsze.

Rozważane algorytmy:

- Regresja logistyczna
- Drzewa decyzyjne (Gradient Boosting)


Oba umożliwiają łatwe wyodrębnienie wag cech.

### 2.3 Kryteria sukcesu

Kryterium biznesowe:
Możliwość wygenerowania raportu "TOP 5 cech" wpływających na długość pobytu

Kryterium analityczne:
- AUC > 0.7

## 3. Analiza dostępnych danych

Na podstawie opisu projektu wiemy, że serwis Nocarz zbiera następujące rodzaje danych:

- szczegółowe dane o lokalach,
- recenzje lokali,
- kalendarz z dostępnością i cenami,
- baza klientów i sesji.

**Dane, które chcielibyśmy wykorzystać**

- Baza klientów/sesji - potencjalnie:
  - kraj/region użytkownika,
  - liczba wcześniejszych rezerwacji,
  - częstotliwość korzystania z serwisu,
  - historia przeglądania ofert
 
  Przykład interpretacji:
  - Klient, który przegląda oferty z dużym wyprzedzeniem i w środku tygodnia, może planować dłuższy wyjazd (np. praca zdalna).
  - Klient, który często wraca do jednego regionu, może preferować dłuższe pobyty w znanym miejscu.

- Dane kalendarzowe
  - daty rezerwacji,
  - długość pobytu,
  - historia cen dla danej oferty,
  - sezonowość:
    - miesiąc, dzień tygodnia,
    - okresy specjalne (wakacje, ferie, święta).

- Dane o lokalach
  - typ obiektu: mieszkanie, dom, pokój, apartament,
  - lokalizacja: miasto, region, odległość od centrum/atrakcji,
  - maksymalna liczba osób, liczba pokoi,
  - cechy standardu i wyposażenia.

- Recenzje lokali
  - średnia ocena,
  - liczba recenzji


**Luki w danych i potrzebne uzupełnienia**

Brak lub nieustrukturyzowane dane o wyposażeniu

   - Potrzebujemy dobrze zdefiniowanych, ustrukturyzowanych flag binarnych typu:
     - `has_fast_wifi`,
     - `has_kitchen`,
     - `has_washing_machine`,
     - `has_workspace`,
     - `is_kid_friendly` ,
     - `has_free_parking` 




