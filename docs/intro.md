---
title: "Dokumentacja wstępna: Analiza długich rezerwacji (zadanie 7)"
author:
  - "Damian D'Souza"
  - "Kamil Marszałek"
date: "2025-11-27"
---

## 1. Definicja problemu

Obecnie brakuje nam wiedzy o czynnikach, które wpływają na długość rezerwacji. Nie wiemy, dlaczego niektórzy klienci rezerwują noclegi na dłuższe okresy (np. 7 dni+).

To utrudnia pracę Konsultantom - nie mogą skutecznie doradzać właścicielom, jakie udogodnienia warto dodać, żeby przyciągnąć klientów szukających dłuższych pobytów.

**Cel projektu:** Zidentyfikować kluczowe czynniki (cechy oferty i profilu klienta), które zwiększają prawdopodobieństwo długiej rezerwacji. Dzięki temu Konsultanci będą mogli konkretnie wskazać oferentom, co zmienić w ofercie (np. dodać szybkie Wi-Fi, wprowadzić rabaty tygodniowe), żeby zwiększyć szansę na dłuższe rezerwacje.

## 2. Podejście modelowe

**Co modelujemy:**

- Zmienna binarna: Rezerwacja "Długa" (1) vs "Krótka" (0)
- Robocza definicja długiej rezerwacji: pobyt np. powyżej 7 dni
- **Wymaga potwierdzenia:** Czy próg 7 dni jest odpowiedni?

**Wybór modelu:**
Potrzebujemy modelu interpretowalnego, który pozwoli zrozumieć, które cechy są najważniejsze.

Rozważane algorytmy:

- Drzewa decyzyjne
- Regresja logistyczna

Oba umożliwiają łatwe wyodrębnienie wag cech.

**Kryteria sukcesu:**

Możliwość wygenerowania raportu "TOP 5 cech" wpływających na długość pobytu

## 3. Analiza dostępnych danych

### Dane, które mamy

**Baza klientów/sesji:**

- Informacje o lokalizacji użytkowników
- Historia przeglądania ofert
- Przykład użycia: Klient szukający w środku tygodnia z dużego miasta prawdopodobnie planuje pracę zdalną

**Dane kalendarzowe:**

- Daty rezerwacji
- Historia cen

### Luki w danych i potrzebne uzupełnienia

**1. Szczegóły wyposażenia**

- **Potrzebujemy:** Ustrukturyzowanych danych o wyposażeniu w formie binarnych flag, przykładowe dane:
  - `has_fast_wifi` (szybki internet)
  - `has_washing_machine` (pralka)
  - `has_dishwasher` (zmywarka)
