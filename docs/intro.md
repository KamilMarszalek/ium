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

- Rodzaj zadania: klasyfikacja binarna.

### 2.2 Wybór modelu

Potrzebujemy modelu interpretowalnego, który pozwoli zrozumieć, które cechy są najważniejsze.

Rozważane algorytmy:

- Regresja logistyczna
- Drzewa decyzyjne (Gradient Boosting)

Oba umożliwiają łatwe wyodrębnienie wag cech.

### 2.3 Kryteria sukcesu

#### 2.3.1 Kryterium biznesowe

**Cel biznesowy:** Dostarczenie konsultantom konkretnych, wdrożeniowych rekomendacji dla właścicieli nieruchomości co pozwoli zwiększyć liczbę długich rezerwacji o 15%.

**Mierniki sukcesu biznesowego:**

- Model identyfikuje minimum 3-5 kluczowych cech, które właściciele mogą zmodyfikować (np. dodanie Wi-Fi, wyposażonej kuchni)
- Rekomendacje są zrozumiałe dla konsultantów bez technicznego background'u

#### 2.3.2 Kryterium analityczne

**Metryki:**
Ze względu na potencjalnie niezbalansowane dane (długie rezerwacje mogą być rzadsze), używamy metryk odpornych na dysproporcje klas:

- **ROC AUC** - główna metryka
- **PR AUC** - metryka uzupełniająca, szczególnie ważna przy silnie niezbalansowanych danych, gdzie ROC AUC może dawać fałszywie optymistyczne wyniki

**Model bazowy do porównania:**

**Model większościowy** - zawsze przewiduje klasę większościową (najprawdopodobniej "krótka rezerwacja"). Taki model osiąga ROC AUC ok. 0.5 (równoważne losowemu zgadywaniu).

**Cel analityczny:**

Model musi spełniać następujące kryteria:

- **Przewidywalność:** Wykazać, że długość rezerwacji jest w ogóle przewidywalna na podstawie dostępnych danych
- **Praktyczna użyteczność:** Osiągnąć **ROC AUC > 0.7**, co oznacza wyraźną poprawę względem modelu bazowego (0.5) i wskazuje na realną wartość predykcyjną
- **Interpretowalność:** Umożliwić identyfikację najważniejszych cech z jasną interpretacją ich wpływu

**Proces ustalania progów:**

1. **Analiza danych:**
   - Zbadanie rozkładu klas (% długich vs. krótkich rezerwacji)
   - Ocena jakości i kompletności danych

2. **Wstępne modelowanie:**
   - Zbudowanie prostego modelu
   - Ustalenie baseline'u dla ROC AUC
   - Ocena czy problem jest w ogóle przewidywalny

3. **Ustalenie progów:**
   - Na podstawie baseline'u określenie realistycznego celu
   - Walidacja czy osiągnięta skuteczność przekłada się na wartość biznesową (czy zidentyfikowane czynniki są modyfikowalne przez właścicieli)
