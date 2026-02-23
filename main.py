from bs4 import BeautifulSoup

class PunktGraniczny:
    def __init__(self, geometria, idPunktu,
                 sposobPozyskania, spelnienieWarunkowDokl,
                 rodzajStabilizacji, oznWMaterialeZrodlowym,
                 numerOperatuTechnicznego, dodatkoweInformacje):
        self.geometria = geometria
        self.idPunktu = idPunktu
        self.sposobPozyskania = sposobPozyskania
        self.spelnienieWarunkowDokl = spelnienieWarunkowDokl
        self.rodzajStabilizacji = rodzajStabilizacji
        self.oznWMaterialeZrodlowym = oznWMaterialeZrodlowym
        self.numerOperatuTechnicznego = numerOperatuTechnicznego
        self.dodatkoweInformacje = dodatkoweInformacje


class DzialkaEwidencyjna:
    def __init__(self, idDzialki, geometria, numerKW,
                 poleEwidencyjne, obreb_id, jednostka_id):
        self.idDzialki = idDzialki
        self.nrDzialki = idDzialki.split('.')[-1]
        self.geometria = geometria
        self.numerKW = numerKW
        self.poleEwidencyjne = poleEwidencyjne
        self.obreb_id = obreb_id
        self.jednostka_id = jednostka_id
        self.punktyGraniczne = []
        self.budynki = []


class Budynek:
    def __init__(self, idBudynku, geometria, rodzajWgKST,
                 kondNadziemne, kondPodziemne,
                 powZabudowy, dzialka_id):
        self.idBudynku = idBudynku
        self.geometria = geometria
        self.rodzajWgKST = rodzajWgKST
        self.kondNadziemne = kondNadziemne
        self.kondPodziemne = kondPodziemne
        self.powZabudowy = powZabudowy
        self.dzialka_id = dzialka_id
        self.obiekty_trwale = []


class ObiektTrwaleZwiazany:
    def __init__(self, geometria, rodzaj):
        self.geometria = geometria
        self.rodzaj = rodzaj


class KonturUzytku:
    def __init__(self, geometria, OFU, obreb_id):
        self.geometria = geometria
        self.OFU = OFU
        self.obreb_id = obreb_id


class KonturKlasyfikacyjny:
    def __init__(self, geometria, OZU, OZK, obreb_id):
        self.geometria = geometria
        self.OZU = OZU
        self.OZK = OZK
        self.obreb_id = obreb_id


class JednostkaEwidencyjna:
    def __init__(self, idJednostkiEwid, geometria, nazwaWlasna):
        self.idJednostkiEwid = idJednostkiEwid
        self.geometria = geometria
        self.nazwaWlasna = nazwaWlasna


class ObrebEwidencyjny:
    def __init__(self, idObrebu, geometria, nazwaWlasna, jednostka_ref):
        self.idObrebu = idObrebu
        self.geometria = geometria
        self.nazwaWlasna = nazwaWlasna
        self.jednostka_ref = jednostka_ref



def read_gml(path):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")

    jednostki = {}
    obreby = {}
    dzialki = {}
    budynki = {}
    uzytki = []
    klasyfikacja = []

    # JEDNOSTKI
    for j in soup.find_all("egb:EGB_JednostkaEwidencyjna"):
        jednostki[j.get("gml:id")] = JednostkaEwidencyjna(
            j.find("egb:idJednostkiEwid").text,
            j.find("egb:geometria").text,
            j.find("egb:nazwaWlasna").text
        )

    # OBRĘBY
    for o in soup.find_all("egb:EGB_ObrebEwidencyjny"):
        obreby[o.get("gml:id")] = ObrebEwidencyjny(
            o.find("egb:idObrebu").text,
            o.find("egb:geometria").text,
            o.find("egb:nazwaWlasna").text,
            o.find("egb:lokalizacjaObrebu").get("xlink:href")
        )

    for d in soup.find_all("egb:EGB_DzialkaEwidencyjna"):
        obreb_ref = d.find("egb:lokalizacjaDzialki").get("xlink:href")
        jednostka_ref = obreby[obreb_ref].jednostka_ref if obreb_ref in obreby else ""

        dz = DzialkaEwidencyjna(
            d.find("egb:idDzialki").text,
            d.find("egb:geometria").text,
            d.find("egb:numerKW").text if d.find("egb:numerKW") else "",
            d.find("egb:poleEwidencyjne").text,
            obreb_ref,
            jednostka_ref
        )

        for p in d.find_all("egb:punktGranicyDzialki"):
            ref = p.get("xlink:href")
            pkt = soup.find("egb:EGB_PunktGraniczny", {"gml:id": ref})
            if pkt:
                dz.punktyGraniczne.append(
                    PunktGraniczny(
                        pkt.find("egb:geometria").text,
                        pkt.find("egb:idPunktu").text,
                        pkt.find("egb:sposobPozyskania").text if pkt.find("egb:sposobPozyskania") else "",
                        pkt.find("egb:spelnienieWarunkowDokl").text if pkt.find("egb:spelnienieWarunkowDokl") else "",
                        pkt.find("egb:rodzajStabilizacji").text if pkt.find("egb:rodzajStabilizacji") else "",
                        pkt.find("egb:oznWMaterialeZrodlowym").text if pkt.find("egb:oznWMaterialeZrodlowym") else "",
                        pkt.find("egb:numerOperatuTechnicznego").text if pkt.find("egb:numerOperatuTechnicznego") else "",
                        pkt.find("egb:dodatkoweInformacje").text if pkt.find("egb:dodatkoweInformacje") else ""
                    )
                )

        dzialki[d.get("gml:id")] = dz


    for b in soup.find_all("egb:EGB_Budynek"):
        dz_ref = b.find("egb:dzialkaZabudowana").get("xlink:href")

        bud = Budynek(
            b.find("egb:idBudynku").text,
            b.find("egb:geometria").text,
            b.find("egb:rodzajWgKST").text,
            b.find("egb:liczbaKondygnacjiNadziemnych").text if b.find("egb:liczbaKondygnacjiNadziemnych") else "",
            b.find("egb:liczbaKondygnacjiPodziemnych").text if b.find("egb:liczbaKondygnacjiPodziemnych") else "",
            b.find("egb:powZabudowy").text if b.find("egb:powZabudowy") else "",
            dz_ref
        )

        budynki[b.get("gml:id")] = bud
        if dz_ref in dzialki:
            dzialki[dz_ref].budynki.append(bud)

    # OBIEKTY TRWALE
    for o in soup.find_all("egb:EGB_ObiektTrwaleZwiazanyZBudynkiem"):
        bud_ref = o.find("egb:budynekZElementamiZwiazanymi").get("xlink:href")
        if bud_ref in budynki:
            budynki[bud_ref].obiekty_trwale.append(
                ObiektTrwaleZwiazany(
                    o.find("egb:geometria").text,
                    o.find("egb:rodzajObiektuZwiazanegoZBudynkiem").text
                )
            )


    for u in soup.find_all("egb:EGB_KonturUzytkuGruntowego"):
        loc = u.find("egb:lokalizacjaKonturu")
        ref = loc.get("xlink:href") if loc else "brak"
        uzytki.append(
            KonturUzytku(
                u.find("egb:geometria").text,
                u.find("egb:OFU").text,
                ref
            )
        )

   
    for k in soup.find_all("egb:EGB_KonturKlasyfikacyjny"):
        loc = k.find("egb:lokalizacjaKonturu")
        obreb_ref = loc.get("xlink:href") if loc else None

        if obreb_ref:
            klasyfikacja.append(
                KonturKlasyfikacyjny(
                    k.find("egb:geometria").text,
                    k.find("egb:OZU").text,
                    k.find("egb:OZK").text if k.find("egb:OZK") else "",
                    obreb_ref
                )
            )

    return dzialki, list(budynki.values()), uzytki, klasyfikacja, jednostki, obreby
