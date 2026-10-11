#!/usr/bin/env python3
"""Samler ansøgningen for Nældevej 42 som én PDF: del A (ny hal) og del B (tilbygning), efterfulgt af tegningsbilag.

Kør:  python3 ansoegning/landzoneansoegning.py
Giver: ansoegning/Landzoneansoegning_Naeldevej_42.pdf  (og ansoegning/ansoegning_tekst.pdf med teksten alene)

Teksten står i listen INDHOLD nedenfor. Felter i [kantede parenteser] skal udfyldes eller bekræftes, før der sendes.
Tegningerne hentes fra tegninger/ og skal være genereret først.
"""
import subprocess
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HER = Path(__file__).parent
TEGN = HER.parent / "tegninger"
DATO = "[dato]"

# Hver post: ("h1"|"h2"|"p"|"li"|"tabel"|"luft", indhold)
INDHOLD = [
    ("h1", "Ansøgning: ny hal og tilbygning til stuehus"),
    ("p", "Nældevej 42, 9000 Aalborg. Matr.nr. 1cc Restrup Hgd., Sønderholm m.fl. BFE-nr. 1416157 m.fl."),
    ("p", f"Til Aalborg Kommune, By og Land, Byggeri, att. Kirstine Reese. {DATO}."),
    ("p", "Ansøgere og ejere: [navne], Nældevej 42, 9000 Aalborg. Telefon [nr.], e-mail [adresse]."),
    ("h2", "1. Hvad ansøgningen omfatter"),
    ("p", "Ansøgningen følger op på mødet den [dato] og jeres mail med gennemgang af praksis. Den har to dele, som vi beder kommunen behandle samlet, fordi de tilsammen viser, hvordan ejendommens bebyggelse kommer til at se ud:"),
    ("tabel", [("Del A: Ny hal", "200 m² hal til maskiner til ejendommens drift og til privat opbevaring. Vi søger landzonetilladelse efter planlovens § 35, stk. 1. Hallen opføres først"),
               ("Del B: Tilbygning", "123 m² tilbygning til stuehuset, så boligen bliver ca. 246 m². Vi mener ikke, den kræver landzonetilladelse, jf. planlovens § 36, stk. 1, nr. 10, og beder kommunen bekræfte det. Tilbygningen opføres senere")]),
    ("p", "Byggetilladelse til begge dele søges særskilt."),
    ("h2", "2. Ejendommen"),
    ("tabel", [("Areal", "39.130 m² (ca. 3,9 ha): matr.nr. 1cc (19.977 m²), 1rp (5.516 m²) og 57b (13.637 m²)"),
               ("Zone og notering", "Landzone. [Noteret som landbrugsejendom / ikke landbrugsnoteret: bekræftes]"),
               ("Anvendelse", "Bolig med hestehold: [antal] heste, stald med 4 hestebokse, 2 ponybokse og løsdrift, ridebane og folde"),
               ("BBR-bygning 4", "Stuehus, 123 m², opført 1992. Én boligenhed"),
               ("BBR-bygning 2", "Bygning til træning og opstaldning af heste, 284 m²"),
               ("Øvrigt", "Skur ved stalden, ca. 23 m², opført efter byggesag S2021-530504 (2020-1967) [BBR-registrering bekræftes]. Ridebane ca. 20 × 39 m med omfangsdræn og pumpe"),
               ("Forsyning", "Privat vandforsyning, jordvarme, privat fællesvej. Spildevand: mekanisk rensning med udledning")]),
    ("side", None),
    ("h2", "3. Planforhold og udpegninger"),
    ("p", "Vi har slået begge placeringer op i Plandata og Danmarks Arealinformation den 10. oktober 2026. Hvor intet andet er nævnt, gælder oplysningen både hal og tilbygning:"),
    ("tabel", [("Plangrundlag", "Landzone. Ingen lokalplan og ingen kommuneplanramme"),
               ("Kommuneplan 2021", "Større sammenhængende landskab. Potentielt naturområde og potentiel økologisk forbindelse (Tostrup og Hasseris Ådal samt Restrup og Sønderholm Skove). Hallens placering ligger desuden i et område, der kan blive udsat for oversvømmelse; det gør tilbygningens ikke"),
               ("Landskabskarakter", "Nørholm Fjordlandskab, jf. kommunens afgørelse for naboejendommen Nældevej 30 (sag S2023-8926) [bekræftes for nr. 42]"),
               ("Ikke udpeget som", "Bevaringsværdigt landskab, lavbundsareal, værdifuldt kulturmiljø, værdifuldt landbrugsområde, skovrejsningsområde eller geologisk bevaringsværdi"),
               ("Kystnærhedszonen", "Ejendommen ligger i kystnærhedszonen, uden for udviklingsområde"),
               ("Skovbyggelinje", "Begge placeringer ligger inden for skovbyggelinjen fra skoven mod øst. Hallen ligger ca. 35 m fra skovbrynet, tilbygningen ca. 80 m. Gives der landzonetilladelse, gælder forbuddet i naturbeskyttelseslovens § 17 ikke, jf. § 17, stk. 2, nr. 5"),
               ("Øvrige linjer", "Uden for sø- og åbeskyttelseslinje, kirkebyggelinje og fredninger. Ingen beskyttede sten- og jorddiger på stedet"),
               ("Beskyttet natur (§ 3)", "Nærmeste er en sø ca. 170 m fra hallen og ca. 210 m fra tilbygningen. Nærmeste beskyttede vandløb ca. 300 m"),
               ("Natura 2000", "Nærmeste område er Nibe Bredning, Halkær Ådal og Sønderup Ådal (habitatområde, fuglebeskyttelses- og Ramsarområde), ca. 1,8 km væk"),
               ("Bilag IV-arter", "Kommunen har i nyere afgørelser på Nældevej (S2024-1080 og S2025-2936) oplyst kendskab til spidssnudet frø, odder, strandtudse, stor vandsalamander og flagermus inden for 2 km. Se afsnit A2")]),

    ("h1", "Del A: Ny hal på 200 m²"),
    ("h2", "A1. Det ansøgte"),
    ("tabel", [("Bygning", "Hal 20,0 × 10,0 m = 200 m², én etage, sadeltag 30° med kip nord-syd. Sidehøjde 4,0 m over soklen, som går 0,4 m over terræn. Kiphøjde 7,3 m over terræn"),
               ("Materialer", "Stålrammer på gennemgående betonsokkel med overkant ca. 0,4 m over terræn, i samme højde som stuehusets sokkel. Facader og tag i sorte, matte sandwichpaneler, som de sorte tage på hus og stald"),
               ("Åbninger", "Port 4,0 × 4,0 m og en gangdør i nordgavlen, mod ejendommens egne bygninger. Ingen åbninger i øvrige facader"),
               ("Placering", "I folden umiddelbart øst for haven, 11,3 m fra stuehuset og 11,4 m fra skuret ved stalden. Parallelt med stalden"),
               ("Maskiner til ejendommens drift, ca. 110 m²", "Traktor med frontlæsser, balletrailer, møgvogn, [harve/slæbeplanke til ridebane, brakpudser, græsslåmaskine: listen bekræftes] og kørebane. "
                "Bruges til foder og strøelse (ca. 25 rundballer om året), udmugning, kørsel til møddingen og pasning af folde og ridebane"),
               ("Privat opbevaring, ca. 90 m²", "Lukket rum på 40 m² med toilet, plads til tre trailere og en lift til hjulskift og vedligehold af husstandens egne biler"),
               ("Eksisterende udhuse", "Ejendommens eneste udhus er skuret på ca. 23 m², som er fyldt med åbnede wrapballer, der skal stå tørt. Der er ingen garage, carport eller maskinhus. Stalden på 284 m² er i brug til hestene: bokse, løsdrift og sadelrum (bilag A3.1)"),
               ("Tagvand", "Tagvand fra hallen (ca. 210 m² tagflade) ledes i lukket rør via en forsinkelsesbrønd til ridebanens eksisterende omfangsdræn og pumpebrønd (ca. 200 l/min), som pumper vandet væk fra arealet [udløbssted oplyses]. Vi søger særskilt om tilladelse, hvis tilslutningen kræver det"),
               ("Opvarmning og afløb", "Uopvarmet hal [bekræftes]. Toilettet tilsluttes [ejendommens eksisterende spildevandsanlæg: afklares]"),
               ("Forplads", "Foran port og dør lægges fliser 50 × 50 cm, som ejendommens øvrige belægning, som en rampe fra gulvhøjde ved gavlen skråt ned til kørevejen, ca. 4 m lang, med fald ud til siderne"),
               ("Adgang", "Ad ejendommens eksisterende kørevej fra Nældevej øst om stalden. Der etableres ikke ny overkørsel til Nældevej")]),
    ("p", "Plantegningen (bilag A1.1) viser, hvad hver maskine og hver funktion fylder. De eksisterende bygninger kan ikke rumme maskinerne: stalden er i brug til hestene rum for rum, som vist på bilag A3.1, "
          "løsdriften bruges med dybstrøelse, og ingen af bygningerne har en port, en traktor kan køre ind ad. Maskiner og trailere står i dag udendørs. "
          "Der drives ikke erhverv fra hallen, og der indrettes ikke bolig."),
    ("p", "Vi søger landzonetilladelse til hele bygningen, så kommunen kan vurdere den samlet. Mener kommunen, at maskindelen kan anmeldes som erhvervsmæssigt nødvendig efter § 36, stk. 1, nr. 3, og § 38, stk. 2, beder vi om at få det oplyst."),
    ("h2", "A2. Begrundelse"),
    ("h3", "Behovet og bygningens størrelse"),
    ("li", "Ejendommen er på 3,9 ha med hestehold, ridebane og folde. Pasningen kræver traktor, balletrailer, møgvogn og redskaber, som bør stå under tag. "
           "Hestehold er hjemmehørende i landzonen, og kommunen har flere gange lagt vægt på netop det, senest i sag S2025-326 og i sag S2022-171976 (Nibevej 384), "
           "hvor en lade på 98 m² til traktor, redskaber, halm og hø blev fundet passende til en ejendom på 1,87 ha med tre heste."),
    ("li", "Vi ved, at kommunen normalt giver tilladelse til udhuse på 50-100 m² og kun til større, når der er særlige omstændigheder. Kommunen ser efter sine afgørelser på ejendommens størrelse, "
           "omfanget af eksisterende udhuse og placeringen. Hos os er ejendommen på 3,9 ha, det eneste udhus er et skur på ca. 23 m², og behovet er vist maskine for maskine på bilag A1.1."),
    ("li", "Kommunen har i nærområdet givet tilladelse til tre bygninger af samme art: "
           "S2025-326 (Nørholmsvej 149, 16. juni 2025): udhus på 148 m² på 2,5 ha med privat hestehold, 104 m² til maskiner og 44 m² til privat værksted. "
           "S2025-10959 (Duedal 93, 21. maj 2026): uopvarmet hal på 150,7 m² med 6,7 m til kip på 1,65 ha, og samtidig en garage på 50 m² ved siden af, fordi der ikke var andre udhuse, og behovet var dokumenteret. "
           "S2023-4703 (Nørholmsvej 222, 20. april 2023): en samlet bygning på 198 m² på 6,3 ha, heraf 120 m² maskinhus og 78 m² udhus."),
    ("li", "Vores hal svarer i opdeling og størrelse til den sidste: ca. 110 m² til maskiner og ca. 90 m² til privat opbevaring. Maskindelen svarer til de 104 m², der blev godkendt i S2025-326 på en mindre ejendom, "
           "og den private del ligger inden for de 50-100 m²."),
    ("li", "Ved at samle maskiner og privat opbevaring under ét tag undgås to fritliggende bygninger, og udendørs oplag af maskiner og trailere forsvinder. "
           "Kommunen lagde i S2023-4703 afgørende vægt på, at sammenbygningen undgår spredt bebyggelse og påvirker landskabet mindre."),
    ("h3", "Placering og landskab"),
    ("li", "Hallen ligger i direkte tilknytning til ejendommens samlede bebyggelse, ca. 11 m fra stuehus og skur, og nås ad den eksisterende kørevej. Det er godt inden for de ca. 20 m, kommunen normalt regner som tilknytning (S2025-6024), og bygninger og færdselsarealer bliver ved med at være én enhed."),
    ("li", "I Nørholm Fjordlandskab bør ny bebyggelse efter kommuneplanen knyttes til de eksisterende bebyggelser og understøtte strukturen af mindre gårde og husmandssteder langs vejene, og det åbne, flade kystlandskab bør bevares. "
           "Hallen lægges inde i en eksisterende gårdbebyggelse ved Nældevej, mellem stuehus, stald og skov, og ikke ud i det åbne land."),
    ("li", "Set fra Nældevej og fra fjorden mod nord ligger hallen bag stald, ridebane og læbælte. Mod vest skærmer læbæltet langs skellet og mod øst skoven. "
           "Hallen slører derfor ikke landskabssammenhængene i det større sammenhængende landskab."),
    ("li", "Kiphøjden på 7,3 m over terræn er under bygningsreglementets 8,5 m og 0,6 m over de 6,7 m, kommunen godkendte i S2025-10959; forskellen er soklen, som følger stuehusets, og hallens større bredde. Sidehøjden på 4,0 m over gulv er bestemt af porten og af frihøjden over traktor med frontlæsser. Facader og tag er sorte og matte, uden reflekser. "
           "Vi planter gerne et læbælte af hjemmehørende arter syd for hallen, hvor den står frit, og holder det i mindst 3 m højde."),
    ("h3", "Kystnærhedszonen"),
    ("li", "Hallen opføres inde i en bestående bebyggelse knap 2 km fra kysten, bag eksisterende bygninger og beplantning set fra kysten, og den ændrer ikke kystlandskabet. "
           "Vi mener derfor, at den har helt underordnet betydning for de nationale planlægningsinteresser i kystområderne, jf. planlovens § 35, stk. 3. "
           "Kommunen har givet tilladelse til udhuse, garager og carporte i samme del af kystnærhedszonen, uden for udviklingsområde, i sagerne S2023-8926 (Nældevej 30), S2024-19470 (Nældevej 55), S2024-1080 (Nældevej 9) og S2025-326."),
    ("h3", "Natur"),
    ("li", "Hallen opføres på en afgræsset fold tæt ved bygninger, kørearealer og ridebane. Der fældes ingen træer og fjernes ingen hegn eller diger. "
           "Med 1,8 km til nærmeste Natura 2000-område og hallens begrænsede omfang kan den ikke påvirke området."),
    ("li", "Bilag IV-arter: Byggefeltet er en tæt afgræsset hestefold uden vandhuller, grøfter, gamle træer eller bygninger, og der er daglig færdsel. Det er ikke egnet som yngle- eller rasteområde for padder, odder eller flagermus. "
           "Nærmeste sø ligger ca. 170 m væk. Der fældes ingen træer og nedrives ingen bygninger, så flagermus mister ikke levesteder, og en bygning på 200 m² inde i bebyggelsen spærrer ikke for dyrs vandring."),
    ("li", "Skovbrynet berøres ikke: der er ca. 35 m fra hallen til skoven, og hallen ligger ikke mellem skoven og åbent land, men ind mod ejendommens bygninger. Den tager derfor ikke udsynet til skoven fra vej eller nabo. "
           "Hele ejendommens bebyggelse ligger inden for skovbyggelinjen, så hallen kan ikke placeres uden for den."),
    ("li", "Den potentielle økologiske forbindelse følger ådalen og skovene. Hallen optager 200 m² af en fold midt i bebyggelsen og spærrer ikke for forbindelsen."),
    ("h3", "Oversvømmelse"),
    ("li", "Hallen er et uopvarmet maskinhus uden beboelse. Soklens overkant og hallens gulv lægges ca. 0,4 m over terræn, i samme højde som stuehusets sokkel [terrænkote indsættes], og kommunen er velkommen til at stille vilkår om sokkelhøjde. Terrænet ændres ikke uden om hallen, og tagvandet ledes til ejendommens eksisterende afløb med pumpe, så der ikke ledes vand mod naboer."),
    ("h3", "Naboer"),
    ("li", "Hallen har ingen åbninger mod naboer. Nærmeste bygning på naboejendom ligger ca. 50 m fra hallen mod sydøst [afstand til nabobeboelse bekræftes], og hallen holder [afstand] m til skel. Naboerne har skriftligt erklæret, at de godkender byggeriet (bilag B2)."),
    ("h2", "A3. Vilkår, vi kan acceptere"),
    ("p", "Hallen bruges ikke til erhverv eller beboelse. Der er ikke udendørs oplag af maskiner, trailere og redskaber. Facader og tag holdes i mørke, ikke-reflekterende farver. "
          "Der plantes og vedligeholdes afskærmende beplantning af hjemmehørende arter syd for hallen i mindst 3 m højde, og de eksisterende læbælter bevares. Vilkårene kan tinglyses på ejendommen."),

    ("h1", "Del B: Tilbygning til stuehuset"),
    ("h2", "B1. Det ansøgte"),
    ("tabel", [("Bygning", "Tilbygning på 123 m² mod vest på stuehuset, én etage. 8,0 m bred og 15,0 m lang; den går 7,0 m forbi husets sydfacade"),
               ("Indhold", "Garage til to biler (45 m²), bad, garderobe, gang og soveværelse (i alt ca. 71 m² opvarmet bolig). Intet køkken"),
               ("Sammenbygning", "Tilbygningen bruger husets vestgavl som fælles væg og har døre til stuen og til bryggerset. Den er en udvidelse af den ene eksisterende bolig"),
               ("Udseende", "Nøjagtig samme stil som huset: hvide vægge, sort bølgepladetag med samme taghældning og kiphøjde (ca. 4,7 m over terræn), samme grå sokkel (ca. 0,4 m), sorte vinduer i husets mål"),
               ("Samlet bolig", "123 m² + 123 m² = ca. 246 m² bruttoetageareal, inklusive den integrerede garage"),
               ("Placering", "Ca. 6,7 m fra skel mod vest [skel bekræftes]. Garageportene vender mod den eksisterende gårdsplads. Garagens gulv ligger i sokkelhøjde som resten af huset, og gruset føres jævnt op til portene"),
               ("Afløb", "Det nye bad tilsluttes [ejendommens eksisterende spildevandsanlæg: afklares]"),
               ("Tidsplan", "Hallen opføres først. Tilbygningen opføres derefter, senest [år]")]),
    ("h2", "B2. Hvorfor vi mener, at tilbygningen ikke kræver landzonetilladelse"),
    ("p", "Efter planlovens § 36, stk. 1, nr. 10, kræves der ikke landzonetilladelse til til- og ombygning af helårshus, når husets samlede bruttoetageareal ikke overstiger 500 m²:"),
    ("li", "Huset er et fritliggende helårshus med én boligenhed, opført 1992 og løbende renoveret."),
    ("li", "Det samlede areal bliver ca. 246 m², under halvdelen af grænsen på 500 m², også når garagen regnes med."),
    ("li", "Der er tale om en tilbygning, som er sammenbygget med huset og deler væg og tag med det. Der indrettes ikke en ekstra bolig; tilbygningen har intet køkken."),
    ("p", "Vi beder kommunen bekræfte, at tilbygningen er omfattet af § 36, stk. 1, nr. 10. Mener kommunen, at den kræver landzonetilladelse, beder vi om, at denne ansøgning også behandles som ansøgning herom."),
    ("h2", "B3. Forholdet til omgivelserne"),
    ("li", "Tilbygningen ligger op ad huset inde i ejendommens bebyggelse, bag læbæltet mod vest, og har samme højde, form og farver som huset. Den ændrer ikke bebyggelsens fremtræden i landskabet."),
    ("li", "Den opføres på eksisterende græsplæne og grus. Der fældes ingen træer. Placeringen ligger ikke i det område, der kan blive udsat for oversvømmelse."),
    ("li", "Vi er opmærksomme på, at vi selv skal sikre, at tilbygningen overholder bygningsreglementets afstands- og højdekrav, og at ejendommens jordvarmeslanger i haven mod vest skal respekteres eller lægges om."),
    ("h2", "B4. Rækkefølge"),
    ("p", "Vi ønsker at bygge hallen først og tilbygningen senere. Vi beder kommunen oplyse, om tilbygningen kan indgå i samme byggetilladelse, eller om vi skal søge byggetilladelse til den, når vi er klar."),

    ("h2", "Bilag"),
    ("tabel", [("A0.1", "Situationsplan 1:500 med hal og tilbygning"), ("A0.2", "Situationsplan på luftfoto (ubebyggede arealer)"),
               ("A1.1", "Hal, plan og indretning 1:100"), ("A1.2", "Hal, facader 1:100"), ("A1.3", "Hal, snit 1:50"),
               ("A2.1", "Hus med tilbygning, plan 1:100"), ("A2.2", "Hus med tilbygning, facader 1:100"), ("A2.3", "Tilbygning, snit 1:50"), ("A3.1", "Stald, eksisterende indretning og brug 1:100"),
               ("B1", "Rumlige skitser fra fire hjørner"), ("B2", "Naboernes skriftlige accept [vedlægges]")]),
    ("luft", 0.012),
    ("p", "Med venlig hilsen"),
    ("p", "[navne]"),
]


def sider():
    """Lægger INDHOLD ud på A4-sider med automatisk sideskift."""
    figs, tilstand = [], {"fig": None, "y": 0.0, "nr": 0}

    def ny():
        fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
        tilstand.update(fig=fig, y=0.945, nr=tilstand["nr"] + 1)
        fig.text(0.92, 0.03, f"Side {tilstand['nr']}", fontsize=7, ha="right", color="#666666")
        fig.text(0.08, 0.03, "Ansøgning: ny hal og tilbygning til stuehus, Nældevej 42, 9000 Aalborg", fontsize=7, color="#666666")
        figs.append(fig)

    def plads(h):
        if tilstand["fig"] is None or tilstand["y"] - h < 0.06:
            ny()

    LH = 0.0142
    ny()
    for type_, v in INDHOLD:
        if type_ == "side":
            ny()
        elif type_ == "luft":
            tilstand["y"] -= v
        elif type_ in ("h1", "h2", "h3"):
            if type_ == "h1" and tilstand["y"] < 0.93:
                ny()
            fs, foer, efter = {"h1": (14, 0.022, 0.032), "h2": (10.5, 0.012, 0.022), "h3": (9, 0.004, 0.018)}[type_]
            plads(efter + foer + 3 * LH)
            tilstand["y"] -= foer
            tilstand["fig"].text(0.08, tilstand["y"], v, fontsize=fs, weight="bold", va="top")
            tilstand["y"] -= efter
        elif type_ in ("p", "li"):
            linjer = textwrap.wrap(v, 108 if type_ == "p" else 104)
            plads(len(linjer) * LH + 0.008)
            if type_ == "li":
                tilstand["fig"].text(0.085, tilstand["y"], "•", fontsize=9, va="top")
            tilstand["fig"].text(0.08 if type_ == "p" else 0.105, tilstand["y"], "\n".join(linjer), fontsize=8.6, va="top", linespacing=1.38)
            tilstand["y"] -= len(linjer) * LH + 0.008
        elif type_ == "tabel":
            for a, b in v:
                la, lb = textwrap.wrap(a, 26), textwrap.wrap(b, 78)
                h = max(len(la), len(lb)) * LH + 0.006
                plads(h)
                tilstand["fig"].text(0.085, tilstand["y"], "\n".join(la), fontsize=8.4, va="top", weight="bold", linespacing=1.38)
                tilstand["fig"].text(0.30, tilstand["y"], "\n".join(lb), fontsize=8.4, va="top", linespacing=1.38)
                tilstand["fig"].add_artist(plt.Line2D([0.08, 0.92], [tilstand["y"] - h + 0.004] * 2, color="#cccccc", lw=0.4))
                tilstand["y"] -= h
            tilstand["y"] -= 0.006
    return figs


tekst_pdf = HER / "ansoegning_tekst.pdf"
with PdfPages(tekst_pdf) as pdf:
    for f in sider():
        pdf.savefig(f)
        plt.close(f)

# Bilag: første side af hver tegning
BILAG = ["situationsplan.pdf", "situationsplan_luftfoto.pdf", "hal_plan.pdf", "hal_facader.pdf", "hal_snit.pdf",
         "tilbygning_plan.pdf", "hus_facader.pdf", "tilbygning_snit.pdf", "stald_plan.pdf", "isometri.pdf"]
dele = [str(tekst_pdf)]
for navn in BILAG:
    ud = HER / f"_bilag_{navn}"
    subprocess.run(["pdfseparate", "-f", "1", "-l", "1", str(TEGN / navn), str(ud)], check=True)
    dele.append(str(ud))
samlet = HER / "Landzoneansoegning_Naeldevej_42.pdf"
subprocess.run(["pdfunite", *dele, str(samlet)], check=True)
for d in dele[1:]:
    Path(d).unlink()
antal = subprocess.run(["pdfinfo", str(samlet)], capture_output=True, text=True).stdout
print(samlet.name, [l for l in antal.splitlines() if l.startswith("Pages")][0])
