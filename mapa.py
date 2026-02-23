from main import read_gml
import folium
from pyproj import Transformer
import argparse
import os
import webbrowser

# ==========================
# ARGPARSE
# ==========================
parser = argparse.ArgumentParser(description="Wizualizacja danych EGiB z pliku GML")
parser.add_argument("plik", help="Ścieżka do pliku GML")
args = parser.parse_args()

gml_path = args.plik

if not os.path.exists(gml_path):
    print(" Podany plik nie istnieje!")
    exit(1)

output_file = os.path.splitext(os.path.basename(gml_path))[0] + ".html"

transformer = Transformer.from_proj(2178, 4326)

OFU_DESC = {
    "R": "grunty orne",
    "Br": "grunty rolne zabudowane",
    "B": "tereny mieszkaniowe"
}

OZU_DESC = {
    "R": "grunty orne",
    "B": "tereny mieszkaniowe",
    "RV": "grunty orne kl. V"
}

SPOSOB_POZYSKANIA_DESC = {
    "1": "pomiar bezpośredni w terenie",
    "2": "fotogrametria",
    "3": "digitalizacja mapy",
    "4": "inne źródło",
}

SPELNIENIE_WARUNKOW_DOKL_DESC = {
    "1": "spełnia warunki dokładności",
    "2": "nie spełnia warunków dokładności",
}

RODZAJ_STABILIZACJI_DESC = {
    "1": "trwała",
    "2": "nietrwała",
    "3": "brak stabilizacji",
}

def geostring_to_polygons(geo):
    nums = list(map(float, geo.split()))
    pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
    pts = [transformer.transform(x, y) for x, y in pts]

    polygons = []
    current = []

    for p in pts:
        if current and p == current[0]:
            current.append(p)
            polygons.append(current)
            current = []
        else:
            current.append(p)

    if current:
        polygons.append(current)

    return polygons

def geostring_to_coords(geo):
    nums = list(map(float, geo.split()))
    pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
    return [transformer.transform(x, y) for x, y in pts]

def geostring_to_multicoords(geo):
    nums = list(map(float, geo.split()))
    pts = [transformer.transform(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]

    rings = []
    current = []

    for p in pts:
        current.append(p)
        if len(current) > 1 and p == current[0]:
            rings.append(current.copy())
            current = []

    if current:
        rings.append(current)

    return rings

dzialki, budynki, uzytki, klasyf, jednostki, obreby = read_gml(gml_path)

def opis_obreb(obreb_ref):
    if obreb_ref in obreby:
        o = obreby[obreb_ref]
        return f"{o.idObrebu} ({o.nazwaWlasna})"
    return "brak"

def opis_jednostka(obreb_ref):
    if obreb_ref in obreby:
        j_ref = obreby[obreb_ref].jednostka_ref
        if j_ref in jednostki:
            j = jednostki[j_ref]
            return f"{j.idJednostkiEwid} ({j.nazwaWlasna})"
    return "brak"

m = folium.Map(tiles="CartoDB Positron")

fg = {
    "Jednostki": folium.FeatureGroup("Jednostki ewidencyjne"),
    "Obręby": folium.FeatureGroup("Obręby ewidencyjne"),
    "Działki": folium.FeatureGroup("Działki"),
    "Budynki": folium.FeatureGroup("Budynki"),
    "Użytki": folium.FeatureGroup("Użytki"),
    "Klasyfikacja": folium.FeatureGroup("Klasyfikacja"),
    "Punkty": folium.FeatureGroup("Punkty graniczne EGiB"),
    "Obiekty trwale": folium.FeatureGroup("Obiekty trwale związane z budynkami")
}

bounds = []

for j in jednostki.values():
    for poly in geostring_to_polygons(j.geometria):
        bounds.extend(poly)
        folium.Polygon(
            poly,
            color="blue",
            weight=2,
            fill=False,
            popup=f"<b>Jednostka ewidencyjna</b><br>{j.idJednostkiEwid} ({j.nazwaWlasna})"
        ).add_to(fg["Jednostki"])

for o in obreby.values():
    for coords in geostring_to_multicoords(o.geometria):
        bounds.extend(coords)
        folium.Polygon(
            coords,
            color="black",
            weight=2,
            fill=False,
            popup=f"<b>Obręb ewidencyjny</b><br>{o.idObrebu} ({o.nazwaWlasna})"
        ).add_to(fg["Obręby"])

for d in dzialki.values():
    coords = geostring_to_coords(d.geometria)
    bounds.extend(coords)

    folium.Polygon(
        coords,
        color="green",
        weight=2,
        fill=True,
        fillOpacity=0.01,
        popup=f"""
        <b>Działka {d.nrDzialki}</b><br>
        obręb: {opis_obreb(d.obreb_id)}<br>
        jednostka: {opis_jednostka(d.obreb_id)}<br>
        KW: {d.numerKW}<br>
        pole: {d.poleEwidencyjne} ha
        """
    ).add_to(fg["Działki"])

    for p in d.punktyGraniczne:
        pt = geostring_to_coords(p.geometria)
        if not pt:
            continue

        folium.CircleMarker(
            pt[0],
            radius=3,
            color="red",
            fill=True,
            popup=f"""
            <b>Punkt graniczny</b><br>
            ID: {p.idPunktu}<br>
            X: {p.geometria.split()[0]}<br>
            Y: {p.geometria.split()[1]}<br><br>
            <b>Sposób pozyskania:</b> {SPOSOB_POZYSKANIA_DESC.get(p.sposobPozyskania, p.sposobPozyskania)}<br>
            <b>Spełnienie warunków dokładności:</b> {SPELNIENIE_WARUNKOW_DOKL_DESC.get(p.spelnienieWarunkowDokl, p.spelnienieWarunkowDokl)}<br>
            <b>Rodzaj stabilizacji:</b> {RODZAJ_STABILIZACJI_DESC.get(p.rodzajStabilizacji, p.rodzajStabilizacji)}
            """
        ).add_to(fg["Punkty"])

for b in budynki:
    coords = geostring_to_coords(b.geometria)
    bounds.extend(coords)

    folium.Polygon(
        coords,
        color="black",
        weight=3,
        fill=True,
        fillOpacity=0.01,
        popup=f"""
        <b>Budynek</b><br>
        ID budynku: {b.idBudynku}<br>
        ID działki: {b.dzialka_id}<br>
        obręb: {opis_obreb(dzialki[b.dzialka_id].obreb_id)}<br>
        jednostka: {opis_jednostka(dzialki[b.dzialka_id].obreb_id)}<br>
        KST: {b.rodzajWgKST}<br>
        kond. nadz.: {b.kondNadziemne}<br>
        kond. podz.: {b.kondPodziemne}<br>
        pow. zab.: {b.powZabudowy} m²
        """
    ).add_to(fg["Budynki"])

for b in budynki:
    for ot in b.obiekty_trwale:
        coords = geostring_to_coords(ot.geometria)
        bounds.extend(coords)

        folium.Polygon(
            coords,
            color="purple",
            weight=2,
            fill=True,
            fillOpacity=0.4,
            popup=f"""
            <b>Obiekt trwale związany z budynkiem</b><br>
            Rodzaj obiektu: {ot.rodzaj}<br>
            Budynek: {b.idBudynku}
            """
        ).add_to(fg["Obiekty trwale"])

for u in uzytki:
    coords = geostring_to_coords(u.geometria)
    bounds.extend(coords)

    folium.Polygon(
        coords,
        color="#90ee90",
        weight=1,
        fill=True,
        fillOpacity=0.01,
        popup=folium.Popup(f"""
        <div style="font-size:13px">
        <h3>{u.OFU}</h3>
        <b>OFU:</b> {u.OFU} ({OFU_DESC.get(u.OFU, "nieznany")})
        </div>
        """, max_width=300)
    ).add_to(fg["Użytki"])

for k in klasyf:
    coords = geostring_to_coords(k.geometria)
    bounds.extend(coords)

    folium.Polygon(
        coords,
        color="#adfc33",
        weight=1,
        fill=True,
        fillOpacity=0.01,
        popup=f"""
        <b>{k.OZU}{k.OZK}</b><br>
        obręb: {opis_obreb(k.obreb_id)}<br>
        jednostka: {opis_jednostka(k.obreb_id)}<br>
        OZU: {k.OZU} ({OZU_DESC.get(k.OZU, "nieznany")})<br>
        OZK: {k.OZK}
        """
    ).add_to(fg["Klasyfikacja"])

for layer in fg.values():
    layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

if bounds:
    m.fit_bounds(bounds)

m.save(output_file)

print(f"Mapa wygenerowana: {output_file}")

webbrowser.open("file://" + os.path.realpath(output_file))