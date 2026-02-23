#  EGiB GML Vieer



Aplikacja  do wczytywania i wizualizacji danych katastralnych  
**EGiB (Ewidencja Gruntów i Budynków)** z plików GML.

Projekt umożliwia interaktywne przeglądanie działek, budynków, użytków gruntowych, klasyfikacji gleboznawczej oraz punktów granicznych na mapie webowej.

---

##  Opis projektu

Program:

-  Wczytuje plik **GML (EGiB)**
-  Parsuje dane obiektowe (działki, budynki, użytki, klasyfikacje, punkty graniczne)
-  Generuje interaktywną mapę HTML (Folium)
-  Automatycznie otwiera mapę w przeglądarce

Projekt został przygotowany jako narzędzie do analizy i wizualizacji danych ewidencyjnych w formacie GML.

---

##  Warstwy mapy

Mapa zawiera następujące warstwy:

- Jednostki ewidencyjne  
- Obręby ewidencyjne  
-  Działki  
-  Budynki  
-  Użytki gruntowe (OFU)  
-  Klasyfikacja gleboznawcza (OZU/OZK)  
-  Punkty graniczne EGiB  
- Obiekty trwale związane z budynkami  

##  Szybki start


### Zainstaluj zależności

```bash
pip install -r requirements.txt
```

###  Uruchom aplikację

```bash
python mapa.py twoj_plik.gml
```

Po uruchomieniu:

- wygeneruje się plik `twoj_plik.html`
- mapa automatycznie otworzy się w przeglądarce

---

##  Funkcjonalności

###  Działki ewidencyjne
- Numer działki
- Obręb
- Jednostka ewidencyjna
- Numer księgi wieczystej
- Pole ewidencyjne

### Budynki
- ID budynku
- Liczba kondygnacji nadziemnych
- Liczba kondygnacji podziemnych
- Powierzchnia zabudowy
- Powiązanie z działką

###  Użytki gruntowe (OFU)
- Symbol OFU
- Opis rodzaju użytku

###  Klasyfikacja gleboznawcza (OZU/OZK)
- Oznaczenie klasy
- Powiązanie z obrębem i jednostką

###  Punkty graniczne EGiB
- ID punktu
- Współrzędne
- Sposób pozyskania
- Spełnienie warunków dokładności
- Rodzaj stabilizacji

## Struktura projektu

```
egib-gml-viewer/
├── main.py          # Parser GML (BeautifulSoup)
├── mapa.py          # Generowanie mapy (Folium + CLI)
├── dane.gml         # Przykładowy plik GML do uruchomienia programu
├── requirements.txt # Zależności
├── README.md
```
