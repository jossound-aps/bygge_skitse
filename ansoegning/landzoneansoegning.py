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
    ("h1", "Ansøgning om landzonetilladelse: ny hal og tilbygning til stuehus"),
    ("p", "Nældevej 42, 9000 Aalborg. Matr.nr. 1cc, 1rp og 57b Restrup Hgd., Sønderholm. BFE-nr. 1416157 m.fl."),
    ("p", "Til Aalborg Kommune, By og Land, Byggeri."),
    ("p", "Ansøgere og ejere: Julie Vitenson og Jonas Vitenson, Nældevej 42, 9000 Aalborg. Telefon +45 40 15 82 36, e-mail jb@jossound.dk."),
    ("h2", "1. Hvad ansøgningen omfatter"),
    ("p", "Ansøgningen følger op på mødet den [dato] og jeres efterfølgende mail med gennemgang af praksis. Den har to dele, som vi beder kommunen behandle samlet, "
          "fordi de tilsammen viser, hvordan ejendommens bebyggelse kommer til at se ud:"),
    ("tabel", [("Del A: Ny hal", "Hal på 200 m² til maskiner og udstyr til ejendommens drift og hestehold og til privat opbevaring. Vi søger landzonetilladelse efter planlovens § 35, stk. 1. Hallen opføres først"),
               ("Del B: Tilbygning", "Tilbygning på ca. 123 m² til stuehuset, så boligen bliver ca. 246 m². Vi mener ikke, at den kræver landzonetilladelse, jf. planlovens § 36, stk. 1, nr. 10, og beder kommunen bekræfte det. Tilbygningen opføres senere")]),
    ("p", "Byggetilladelse til begge dele søges særskilt, når landzoneforholdene er afklaret."),
    ("h2", "2. Ejendommen"),
    ("tabel", [("Areal", "39.130 m² (ca. 3,9 ha): matr.nr. 1cc (19.977 m²), 1rp (5.516 m²) og 57b (13.637 m²). Stuehus, stald og skur ligger på 1cc, ridebanen på 1rp"),
               ("Zone og notering", "Landzone. [Noteret som landbrugsejendom / ikke landbrugsnoteret: bekræftes]"),
               ("Anvendelse", "Bolig med privat hestehold: [antal] heste, stald med 4 hestebokse, løsdrift og 2 tidligere ponybokse til foder og hesteudstyr, ridebane på ca. 20 × 39 m og folde"),
               ("BBR-bygning 4", "Stuehus, 123 m², opført 1992, ombygget 2024. Én boligenhed"),
               ("BBR-bygning 2", "Bygning til træning og opstaldning af heste, 284 m². Indretning og brug fremgår af bilag A3.1"),
               ("Ridebane og jordfolde", "Ridebanen er ca. 20 × 39 m øst for stalden, med omfangsdræn og pumpe. Den er ikke et nyt anlæg: luftfotoet fra 15. januar 2012 (bilag B2) viser hele arealet øst for stalden som én indhegnet, bar jordbane på ca. 45 × 55 m med heste. "
                "Den tidligere ejer gjorde senere banen mindre og indrettede den sydlige del som jordfolde uden græs til heste med sukkersyge (insulinresistens), som ikke tåler at gå på græs, og lagde sand på den nordlige del. "
                "Ridebane og jordfolde har altså ligget på samme sted i mindst 14 år og er kun blevet mindre"),
               ("Øvrige bygninger", "Skur på ca. 16 m² op ad staldens østside, opført efter byggesag S2021-530504 (2020-1967). Der er ingen garage, carport eller maskinhus på ejendommen"),
               ("Forsyning", "Privat vandforsyning, jordvarme, privat fællesvej. Spildevand: mekanisk rensning med udledning")]),
    ("side", None),
    ("h2", "3. Planforhold og udpegninger"),
    ("p", "Vi har slået begge placeringer op i Plandata og Danmarks Arealinformation den 10. oktober 2026. Hvor intet andet er nævnt, gælder oplysningen både hal og tilbygning:"),
    ("tabel", [("Plangrundlag", "Landzone. Ingen lokalplan og ingen kommuneplanramme"),
               ("Kommuneplanens retningslinjer", "Større sammenhængende landskab. Grønt Danmarkskort: potentielt naturområde og potentiel økologisk forbindelse (Tostrup og Hasseris Ådal samt Restrup og Sønderholm Skove). "
                "Hallens placering ligger desuden i et område, der kan blive udsat for oversvømmelse; det gør tilbygningens ikke"),
               ("Landskabskarakter", "Nørholm Fjordlandskab, som for naboejendommen Nældevej 30 (kommunens afgørelse S2023-8926 af 18. januar 2024)"),
               ("Ikke udpeget som", "Bevaringsværdigt landskab, lavbundsareal, værdifuldt kulturmiljø, værdifuldt landbrugsområde, skovrejsningsområde eller geologisk bevaringsværdi"),
               ("Kystnærhedszonen", "Ejendommen ligger i kystnærhedszonen, uden for udviklingsområde. Afstanden til Limfjorden er ca. 1,9 km"),
               ("Skovbyggelinje", "Begge placeringer ligger inden for skovbyggelinjen fra skoven mod øst, ligesom ejendommens eksisterende bygninger. Hallen ligger ca. 35 m fra skovbrynet, tilbygningen ca. 80 m. "
                "Forbuddet i naturbeskyttelseslovens § 17 gælder ikke for byggeri, der har fået landzonetilladelse, jf. § 17, stk. 2, nr. 5"),
               ("Øvrige linjer", "Uden for sø- og åbeskyttelseslinje, kirkebyggelinje og fredninger. Ingen beskyttede sten- og jorddiger på stedet"),
               ("Beskyttet natur (§ 3)", "Nærmeste er en sø ca. 170 m fra hallen og ca. 210 m fra tilbygningen. Nærmeste beskyttede vandløb ca. 300 m"),
               ("Natura 2000", "Nærmeste område er nr. 15, Nibe Bredning, Halkær Ådal og Sønderup Ådal (habitat-, fuglebeskyttelses- og Ramsarområde), ca. 1,8 km mod nord"),
               ("Bilag IV-arter", "Kommunen har i sine afgørelser for Nældevej 9 (S2024-1080) og Nældevej 37 (S2025-2936) oplyst kendskab til spidssnudet frø, odder, strandtudse, stor vandsalamander og flagermus inden for 2 km. Se afsnit A2")]),

    ("h1", "Del A: Ny hal på 200 m²"),
    ("h2", "A1. Det ansøgte"),
    ("tabel", [("Bygning", "Hal 20,0 × 10,0 m = 200 m², én etage, sadeltag 30° med kip nord-syd. Sidehøjde 4,0 m over soklen, kiphøjde 7,3 m over terræn"),
               ("Materialer", "Stålrammer på gennemgående betonsokkel med overkant ca. 0,4 m over terræn, i samme højde som stuehusets sokkel. Facader og tag i sorte, matte sandwichpaneler, som de sorte tage på stuehus og stald"),
               ("Åbninger", "Port 4,0 × 4,0 m og en gangdør i nordgavlen, som vender mod ejendommens egne bygninger og ridebanen. Ingen åbninger i de øvrige facader"),
               ("Placering", "I folden umiddelbart øst for haven, 11,3 m fra stuehuset og 12,3 m fra skuret ved stalden, parallelt med stald og stuehus. Se bilag A0.1 og A0.2"),
               ("Ejendommens drift og hestehold, ca. 130 m²", "Traktor med frontlæsser, ladtrailer med kapel til hø, halm og wrap, hestetrailer, balleflytter til wrapballer, halmballe-elevator, møgtrailer, en plænetraktor, en havetraktor med rive til at holde gårdsplads og ridebane jævne, og slæbeharve til ridebanen. "
                "Foder og hesteudstyr opbevares i stalden. Maskinerne bruges til foder og strøelse (ca. 25 rundballer om året), udmugning og pasning af folde, ridebane og ejendommens 3,9 ha"),
               ("Privat opbevaring, ca. 70 m²", "Samlet i hallens sydende: et lukket rum på 40 m² med toilet (indretning på bilag A1.6) til lejepresse, værkstedsvogn, sæsonhjul og cykler samt til havemøbler, grill og det øvrige udendørs udstyr, som skal ind om vinteren; plads til en trailer; og en tosøjlet lift til hjulskift og vedligehold af husstandens egne biler"),
               ("Toilet", "Et toilet med håndvask på 1,5 × 1,8 m i det lukkede rum, til brug for dem, der rider og arbejder med hestene og maskinerne. Hverken bad eller køkken"),
               ("Opvarmning og afløb", "Den åbne hal er uopvarmet; det lukkede rum holdes frostfrit. Toilettet tilsluttes ejendommens spildevandsanlæg [afklares]; vi søger særskilt om tilslutningen"),
               ("Tagvand", "Tagvand fra hallen (ca. 210 m² tagflade) ledes i lukket rør via en forsinkelsesbrønd til ridebanens eksisterende omfangsdræn og pumpebrønd (ca. 200 l/min). Vi søger særskilt om tilladelse, hvis tilslutningen kræver det"),
               ("Forplads", "Foran port og dør lægges fliser 50 × 50 cm, som ejendommens øvrige belægning, som en rampe fra gulvhøjde ved gavlen skråt ned til kørevejen, ca. 4 m lang, med fald ud til siderne"),
               ("Matrikler og skel", "Hallen ligger hen over skellet mellem ansøgernes egne matr.nr. 1cc og 1rp, ca. 7 m af bredden på 1cc og ca. 3 m på 1rp. Der er ca. 38 m til nærmeste skel mod nabo. Skellene er vist på bilag A0.1"),
               ("Adgang", "Ad ejendommens eksisterende kørevej fra Nældevej øst om stalden. Der etableres ikke ny overkørsel")]),
    ("p", "Plantegningen (bilag A1.1) viser, hvad hver maskine og hver funktion fylder. De eksisterende bygninger kan ikke rumme maskinerne: stalden er i brug til hestene rum for rum, som vist på bilag A3.1, "
          "løsdriften bruges med dybstrøelse, skuret er fyldt med åbnede wrapballer, og ingen af bygningerne har en port, en traktor kan køre ind ad. Maskiner og trailere står i dag udendørs."),
    ("p", "Hesteholdet er privat. Vi er bekendt med, at et privat hestehold ikke er erhvervsmæssig landbrugsdrift efter planloven, og søger derfor landzonetilladelse efter § 35, stk. 1, til hele hallen. "
          "Der drives ikke erhverv fra hallen."),
    ("h2", "A2. Begrundelse"),
    ("h3", "Behovet"),
    ("li", "Ejendommen er på 3,9 ha med stald, ridebane og folde. Pasningen af hestene og arealerne kræver traktor, trailere til hø, halm og heste, balleflytter, møgtrailer, plænetraktor, havetraktor med rive og ridebaneharve, som i dag står udendørs. "
           "Hver maskine har en fast opgave, og plantegningen viser, at hallen ikke rummer mere end det."),
    ("li", "Kommunen har i to afgørelser i vores område fundet, at et privat hestehold begrunder en bygning til maskinerne. I sag S2022-171976 (Nibevej 384, 13. februar 2023) fik en landbrugsejendom på 1,87 ha med tre heste tilladelse til en lade på 98 m² "
           "til traktor, brakpudser, halm, hø, træningsvogne, seletøj og strøelse; ejendommen brugte ca. 25 rundballer hø om året, som vi. Kommunen lagde vægt på, at et mindre hestehold er hjemmehørende i landzonen, og at laden var passende til ejendommens størrelse. "
           "I sag S2025-326 (Nørholmsvej 149, 16. juni 2025, ca. 900 m herfra) fik en landbrugsejendom på 2,5 ha med privat hobbyhestehold i 4 hestebokse tilladelse til et udhus på 148 m², hvoraf 104 m² til traktor, ATV, slagleklipper, ballespyd, harve og tromle "
           "til vedligehold af ejendommen og 44 m² til privat værksted. Kommunen fandt bygningen passende for en ejendom på over 2,5 ha, hvor de øvrige udhuse var små, og lagde igen vægt på, at heste er hjemmehørende i landzonen."),
    ("li", "Vores ejendom er halvanden gang så stor som Nørholmsvej 149 og dobbelt så stor som Nibevej 384, og vores eneste udhus er et skur på 16 m²."),
    ("h3", "Størrelsen i forhold til kommunens praksis"),
    ("li", "Vi er bekendt med kommunens praksis, som den er gengivet i afgørelserne S2024-1080 og S2025-10959: der gives normalt landzonetilladelse til nye udhuse og garager på 50-100 m², og ved den konkrete vurdering indgår ejendommens størrelse, "
           "omfanget af eksisterende udhuse og placeringen. Ejendommen er på 3,9 ha, det eneste udhus er et skur på 16 m², og hallen ligger 11 m fra stuehuset inde i den samlede bebyggelse."),
    ("li", "Kommunen har godkendt samme størrelse og samme opdeling som vores i sag S2025-10959 (Duedal 93, 21. maj 2026): en uopvarmet hal på 150,7 m² til traktor, rendegraver, minilæsser, havetraktor og andre maskiner til vedligehold af en landbrugsejendom på 1,65 ha uden erhvervsmæssig landbrugsdrift, "
           "og samtidig en garage på 50 m² ved siden af. Kommunen lagde afgørende vægt på, at der ikke var anden udhusbebyggelse på ejendommen, at behovet var dokumenteret, og at bygningen havde en passende størrelse i forhold til ejendommens størrelse og behov for større maskiner til vedligehold af arealet. "
           "Vores hal rummer ca. 130 m² til pasning af ejendommen og hesteholdet, mindre end de 150,7 m² på Duedal 93 og mere end de 104 m² på Nørholmsvej 149, og ca. 70 m² privat, inden for de 50-100 m², kommunen normalt giver tilladelse til. "
           "Vores ejendom er mere end dobbelt så stor som Duedal 93, og vi har heste, som ejendommen dér ikke havde."),
    ("li", "Vi samler det hele under ét tag i stedet for at bygge to bygninger. I sag S2023-4703 (Nørholmsvej 222, 20. april 2023) godkendte kommunen en samlet bygning på 198 m² på en ejendom på 6,3 ha, 120 m² maskinhus og 78 m² udhus, "
           "og lagde afgørende vægt på, at sammenbygningen undgår spredt bebyggelse og påvirker landskabet mindre. Det gælder også her."),
    ("li", "Det private er samlet i hallens sydende og er vist som blå felter på bilag A1.1, så opdelingen kan kontrolleres."),
    ("h3", "Toilettet"),
    ("li", "Når man rider eller arbejder med hestene, er man beskidt af gødning, foder, sved og jord, og det samme gælder arbejdet med maskinerne. Et toilet med håndvask i hallen, lige ved stald og ridebane, betyder, "
           "at man kan gå på toilettet og vaske hænder i ridetøj eller arbejdstøj og støvler uden at skulle ind i stuehuset og gøre det beskidt. "
           "Kommunen har godkendt toilet i et udhus med opbevaring, værksted og garage i sag S2024-7549 (Restrup Kærvej 16, 21. november 2024)."),
    ("li", "Det lukkede rum holdes frostfrit af hensyn til toilettet og vandinstallationen. Den åbne hal er uopvarmet."),
    ("h3", "Placering og landskab"),
    ("li", "Hallen ligger i direkte tilknytning til ejendommens samlede bebyggelse, 11 m fra stuehus og skur, og nås ad den eksisterende kørevej. Det er inden for de ca. 20 m, kommunen efter sin praksis regner som tilknytning (S2025-6024, Munkbækvej 16, 1. oktober 2025), "
           "og bygninger og færdselsarealer udgør fortsat én enhed. I sag S2024-19470 (Nældevej 55, 7. november 2024) lagde kommunen afgørende vægt på, at en carport til traktor, havetraktor og wrapballer til hesteholdet lå ved ejendommens tilkørselsarealer højst 22 m fra stuehuset."),
    ("li", "I Nørholm Fjordlandskab bør ny bebyggelse efter kommuneplanens retningslinje knyttes til de eksisterende bebyggelser langs vejene og understøtte strukturen af mindre gårde og husmandssteder, og det åbne, flade kystlandskab bør bevares. "
           "Hallen lægges inde i en eksisterende gårdbebyggelse ved Nældevej, mellem stuehus, stald og skov, og ikke ud i det åbne land. "
           "Naboejendommen Nældevej 30 har samme udpegninger, og kommunen fandt dér (S2023-8926), at et udhus i tilknytning til bebyggelsen ikke havde væsentlig betydning for dem."),
    ("li", "Ridebanen og jordfoldene, som hallen ligger op ad, har været der siden mindst 2012 og fyldte dengang mere end i dag (bilag B2). Hallen lægges altså i et område, der i mange år har været indhegnet og brugt til hestene, ikke i det åbne land. "
           "Kommunen har selv i sag S2022-180446 (Nørholmsvej 196) lovliggjort en ridebane fra 1992, som også blev brugt som fold til heste med forfangenhed."),
    ("li", "Set fra Nældevej og fra fjorden mod nord ligger hallen bag stald, ridebane og læbælte. Mod vest skærmer læbæltet langs skellet og mod øst skoven. Hallen slører derfor ikke landskabssammenhængene i det større sammenhængende landskab. De rumlige skitser i bilag B1 viser det fra fire sider."),
    ("li", "Kiphøjden på 7,3 m over terræn er under bygningsreglementets 8,5 m. Hallen i sag S2025-10959 er 6,7 m til kip; forskellen hos os er soklen på 0,4 m, som følger stuehusets og hensynet til oversvømmelsesudpegningen, og en sidehøjde på 4,0 m, som porten på 4,0 m og traktoren med frontlæsser kræver. "
           "Facader og tag er sorte og matte, uden reflekser."),
    ("h3", "Kystnærhedszonen"),
    ("li", "Hallen opføres inde i en bestående bebyggelse ca. 1,9 km fra kysten, bag eksisterende bygninger og beplantning set fra fjorden, og den ændrer ikke kystlandskabet. "
           "Vi mener derfor, at den har helt underordnet betydning for de nationale planlægningsinteresser i kystområderne, jf. planlovens § 35, stk. 3. "
           "Kommunen har givet landzonetilladelse til udhuse, garager og carporte i samme del af kystnærhedszonen på Nældevej 30 (S2023-8926), Nældevej 55 (S2024-19470) og Nældevej 9 (S2024-1080) samt på Nørholmsvej 149 (S2025-326)."),
    ("h3", "Natur"),
    ("li", "Hallen opføres på en afgræsset fold tæt ved bygninger, kørearealer og ridebane. Der fældes ingen træer og fjernes ingen hegn eller diger. "
           "Med 1,8 km til nærmeste Natura 2000-område og hallens begrænsede omfang kan den hverken alene eller sammen med andre planer og projekter påvirke området."),
    ("li", "Bilag IV-arter: Byggefeltet er en tæt afgræsset hestefold uden vandhuller, grøfter, gamle træer eller bygninger, og der er daglig færdsel af mennesker og heste. Det er ikke egnet som yngle- eller rasteområde for padder, odder eller flagermus. "
           "Nærmeste sø ligger ca. 170 m væk, med ejendommens bygninger imellem. Der fældes ingen træer og nedrives ingen bygninger, så flagermus mister ikke levesteder, og en bygning på 200 m² inde i bebyggelsen spærrer ikke for dyrs vandring. "
           "Kommunen nåede samme resultat for ridebanen på Nældevej 37 (S2025-2936), som ligger 300 m herfra i samme landskab."),
    ("li", "Skovbrynet berøres ikke: der er ca. 35 m fra hallen til skoven, og hallen ligger ikke mellem skoven og det åbne land, men ind mod ejendommens bygninger. Den tager derfor ikke udsynet til skoven fra vej eller nabo. "
           "Hele ejendommens bebyggelse ligger inden for skovbyggelinjen, så hallen kan ikke placeres uden for den."),
    ("li", "Den potentielle økologiske forbindelse følger ådalen og skovene. Hallen optager 200 m² af en fold midt i bebyggelsen og spærrer ikke for forbindelsen."),
    ("h3", "Oversvømmelse"),
    ("li", "Soklens overkant og hallens gulv lægges ca. 0,4 m over terræn, i samme højde som stuehusets sokkel [terrænkote indsættes], og kommunen er velkommen til at stille vilkår om sokkelhøjde. "
           "Terrænet ændres ikke uden om hallen, og tagvandet ledes til ejendommens eksisterende dræn og pumpe, så der ikke ledes vand mod naboer."),
    ("h3", "Naboer"),
    ("li", "Hallen har ingen åbninger mod naboer. Nærmeste bygning på en naboejendom ligger ca. 50 m fra hallen mod sydøst [afstand til nabobeboelse bekræftes], og der er ca. 38 m til nærmeste skel mod nabo."),
    ("h3", "Matrikler"),
    ("li", "Matr.nr. 1rp ligger omgivet af 1cc og rummer ridebanen og en del af foldene. Alle tre matrikler ejes af ansøgerne og drives som én ejendom. "
           "[Afklares: om 1rp og 1cc er noteret som én samlet fast ejendom. Er de ikke det, lægger vi matriklerne sammen ved landinspektør, før hallen opføres, og accepterer det som vilkår.]"),
    ("h2", "A3. Vilkår, vi kan acceptere"),
    ("p", "At facader og tag holdes i mørke, ikke-reflekterende farver, og at der ikke er udendørs oplag af maskiner, trailere og redskaber."),

    ("h1", "Del B: Tilbygning til stuehuset"),
    ("h2", "B1. Det ansøgte"),
    ("tabel", [("Bygning", "Tilbygning på ca. 123 m² brutto mod vest på stuehuset, én etage. 15,0 m lang og 8,0 m bred langs huset; syd for huset 8,45 m, fordi tilbygningens østvæg står uden på husets gavl. Den går 7,0 m forbi husets sydfacade"),
               ("Indhold", "Garage til to biler (ca. 45 m²), bad (ca. 11 m²), garderobe (ca. 12 m²), gang (ca. 4 m²) og soveværelse (ca. 32 m²). Opvarmet bolig ca. 71 m². Intet køkken"),
               ("Sammenbygning", "Tilbygningen bruger husets vestgavl som fælles væg og får døre til stuen og til bryggerset. Den er en udvidelse af den eksisterende bolig"),
               ("Udseende", "Samme stil som huset: hvide vægge, sort bølgepladetag med samme taghældning og kiphøjde (ca. 4,7 m over terræn), samme grå sokkel (ca. 0,4 m) og sorte vinduer i husets mål. Se bilag A2.1-A2.3"),
               ("Samlet bolig", "123 m² (BBR) + ca. 123 m² = ca. 246 m² bruttoetageareal, inklusive den integrerede garage"),
               ("Placering", "På matr.nr. 1cc, ca. 4,9 m fra skellet mod vest (matr.nr. 1cb). Garageportene vender mod gårdspladsen; garagens gulv ligger i sokkelhøjde, og gruset føres jævnt op til portene"),
               ("Afløb", "Det nye bad tilsluttes ejendommens spildevandsanlæg [afklares]"),
               ("Tidsplan", "Hallen opføres først. Tilbygningen opføres derefter, senest [år]")]),
    ("h2", "B2. Hvorfor tilbygningen ikke kræver landzonetilladelse"),
    ("p", "Efter planlovens § 36, stk. 1, nr. 10, kræves der ikke landzonetilladelse til til- og ombygning af et helårshus, hvorved husets samlede bruttoetageareal ikke overstiger 500 m²:"),
    ("li", "Huset er et fritliggende helårshus med én boligenhed, opført 1992."),
    ("li", "Det samlede areal bliver ca. 246 m², under halvdelen af grænsen på 500 m², også når garagen regnes med."),
    ("li", "Tilbygningen er sammenbygget med huset og deler væg og tag med det."),
    ("p", "Vi beder kommunen bekræfte, at tilbygningen er omfattet af § 36, stk. 1, nr. 10. Mener kommunen, at den kræver landzonetilladelse, beder vi om, at denne ansøgning også behandles som ansøgning om det."),
    ("h2", "B3. Forholdet til omgivelserne"),
    ("li", "Tilbygningen ligger op ad huset inde i ejendommens bebyggelse, bag læbæltet mod vest, og har samme højde, form og farver som huset. Den ændrer ikke bebyggelsens fremtræden i landskabet."),
    ("li", "Den opføres på eksisterende græsplæne og grus. Der fældes ingen træer. Placeringen ligger ikke i det område, der kan blive udsat for oversvømmelse."),
    ("li", "Vi sikrer selv, at tilbygningen overholder bygningsreglementets afstands- og højdekrav, og at ejendommens jordvarmeslanger i haven mod vest respekteres eller lægges om."),
    ("h2", "B4. Rækkefølge"),
    ("p", "Vi ønsker at bygge hallen først og tilbygningen senere. Vi beder kommunen oplyse, om tilbygningen kan indgå i samme byggetilladelse, eller om vi skal søge byggetilladelse til den, når vi er klar."),

    ("h2", "Bilag"),
    ("tabel", [("A0.1", "Situationsplan 1:500 med hal, tilbygning og matrikelskel"), ("A0.2", "Situationsplan på luftfoto"),
               ("A1.1", "Hal, plan og indretning 1:100"), ("A1.2", "Hal, facader 1:100"), ("A1.3", "Hal, snit 1:50 med hovedresultater"), ("A1.4", "Hal, konstruktionsplaner 1:100"),
               ("A1.5", "Hal, foreløbig overslagsberegning. Producentens endelige beregning følger i byggeansøgningen"), ("A1.6", "Hal, det lukkede rum: plan 1:50 og perspektiv"),
               ("A2.1", "Hus med tilbygning, plan 1:100"), ("A2.2", "Hus med tilbygning, facader 1:100"), ("A2.3", "Tilbygning, snit 1:50 med hovedresultater"), ("A2.4", "Tilbygning, foreløbig overslagsberegning. Spærfabrikkens endelige beregning følger i byggeansøgningen"),
               ("A3.1", "Stald, eksisterende indretning og brug 1:100"),
               ("B1", "Rumlige skitser fra fire hjørner"), ("B2", "Historiske luftfotos 2012-2026 af stald og ridebane")]),
    ("luft", 0.012),
    ("p", "Med venlig hilsen"),
    ("p", "Julie Vitenson og Jonas Vitenson"),
]


def sider():
    """Lægger INDHOLD ud på A4-sider med automatisk sideskift."""
    figs, tilstand = [], {"fig": None, "y": 0.0, "nr": 0}

    def ny():
        fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
        tilstand.update(fig=fig, y=0.945, nr=tilstand["nr"] + 1)
        fig.text(0.92, 0.03, f"Side {tilstand['nr']}", fontsize=7, ha="right", color="#666666")
        fig.text(0.08, 0.03, "Ansøgning om landzonetilladelse, Nældevej 42, 9000 Aalborg", fontsize=7, color="#666666")
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
# (fil, alle sider?) – tegningerne tages kun med første side; beregningsrapporterne med alle sider
BILAG = [("situationsplan.pdf", False), ("situationsplan_luftfoto.pdf", False), ("hal_plan.pdf", False), ("hal_facader.pdf", False), ("hal_snit.pdf", False),
         ("hal_konstruktion.pdf", False), ("hal_beregning.pdf", True), ("hal_rum.pdf", False), ("tilbygning_plan.pdf", False), ("hus_facader.pdf", False), ("tilbygning_snit.pdf", False),
         ("tilbygning_beregning.pdf", True), ("stald_plan.pdf", False), ("isometri.pdf", False), ("luftfoto_historisk.pdf", False)]
dele = [str(tekst_pdf)]
for navn, alle in BILAG:
    if alle:
        dele.append(str(TEGN / navn))
        continue
    ud = HER / f"_bilag_{navn}"
    subprocess.run(["pdfseparate", "-f", "1", "-l", "1", str(TEGN / navn), str(ud)], check=True)
    dele.append(str(ud))
samlet = HER / "Landzoneansoegning_Naeldevej_42.pdf"
subprocess.run(["pdfunite", *dele, str(samlet)], check=True)
for d in dele[1:]:
    if Path(d).name.startswith("_bilag_"):
        Path(d).unlink()
antal = subprocess.run(["pdfinfo", str(samlet)], capture_output=True, text=True).stdout
print(samlet.name, [l for l in antal.splitlines() if l.startswith("Pages")][0])
