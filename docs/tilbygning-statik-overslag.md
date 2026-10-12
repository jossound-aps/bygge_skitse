# Foreløbig overslagsberegning for tilbygningens tagkonstruktion

Nældevej 42, 9000 Aalborg. 11. oktober 2026. Hører til tegningerne A2.2 og A2.3.

**Beregningen er foreløbig.** Den er udført af bygherren som grundlag for landzoneansøgningen og viser, at tilbygningen kan udføres med gitterspær som i det eksisterende hus. Gitterspærene dimensioneres og leveres af en spærfabrik, som udarbejder den endelige beregning og monteringsvejledning til byggeansøgningen.

Beregningen følger DS/EN 1990, DS/EN 1991-1-3 og DS/EN 1991-1-4 med de danske nationale annekser (DK NA 2024 for sne og vind) og DS/EN 1995-1-1. Spæret er regnet som plan gitterkonstruktion (elementmetode), og lastkombinationerne er dannet efter DS/EN 1990 DK NA, ligning 6.10b.

## 1. Det eksisterende hus

Billederne fra loftet (billeder/IMG_2987-2989) viser W-gitterspær i træ: gennemgående spærhoved og spærfod, to trækdiagonaler fra spærfoden op til kippen og to trykstivere ud til midten af spærhovederne. Spærene står med ca. 1 m afstand og bærer lægter og sorte bølgeplader. Loftet er isoleret på spærfoden og bruges til opbevaring. Tilbygningen er forudsat udført på samme måde, så tag og loft kan føres igennem i samme stil.

## 2. Forudsætninger

| | |
|---|---|
| Spærtype | W-gitterspær, konstruktionstræ C24, samlet med tandplader |
| Spændvidde | 8,0 m mellem vægmidter (den sydlige del, hvor tilbygningen har egne vægge i begge sider) |
| Taghældning og spærafstand | 25° og 1,0 m, som anslået for det eksisterende hus |
| Egenlast | Tag 0,35 kN/m² (bølgeplader, lægter, spær), loft 0,35 kN/m² (isolering og loftbeklædning) |
| Nyttelast på loft | 0,5 kN/m² til let opbevaring (antaget; ψ0 = 0,5 som for kategori A i DS/EN 1990 DK NA) |
| Sne | s_k = 1,0 kN/m² (DK NA); jævn μ_1 = 0,8 (tabel 5.2); ophobning på vestlig tagflade μ_w = 1,2 efter DK NA 5.3.3(4), fordi tilbygningens kip ligger nord-syd og den østlige tagflade vender mod øst. Medtaget på den sikre side |
| Vind | q_p = 0,67 kN/m² i 4,7 m højde (v_b,0 = 24 m/s, terrænkategori II); sug på hele taget med c_pe = −0,8 (DS/EN 1991-1-4 tabel 7.4a, zone F/G ved 25°, på den sikre side) og c_pi = +0,2, i alt −1,0 |
| Træ | C24 (DS/EN 338): f_m = 24, f_c,0 = 21, f_t,0 = 14,5 MPa, E_0,05 = 7.400 MPa; k_mod = 0,9 (korttidslast, anvendelsesklasse 2); γ_M = 1,35 (DS/EN 1995-1-1 DK NA). Søjlereduktion k_c efter DS/EN 1995-1-1, 6.3.2 |

## 3. Dimensioner

Udnyttelse for tryk eller træk kombineret med bøjning. Trykstænger er regnet med søjlevirkning; spærhovedet fastholdes sideværts af lægterne.

| Spærhoved | Spærfod | Gitterstænger | Udnyttelse hoved | fod | gitter | Opfylder |
|---|---|---|---|---|---|---|
| 45 × 120 | 45 × 95 | 45 × 70 | 0,88 | 0,80 | 0,28 | ja |
| 45 × 145 | 45 × 120 | 45 × 95 | 0,58 | 0,56 | 0,20 | ja |
| 45 × 170 | 45 × 120 | 45 × 95 | 0,44 | 0,54 | 0,20 | ja |
| 45 × 195 | 45 × 145 | 45 × 95 | 0,35 | 0,40 | 0,19 | ja |
| 45 × 220 | 45 × 145 | 45 × 120 | 0,30 | 0,40 | 0,15 | ja |

**Mindste sæt, der opfylder overslaget: spærhoved 45 × 120 mm, spærfod 45 × 95 mm, gitterstænger 45 × 70 mm.** Samlingerne (tandplader) er ikke regnet og er ofte det, der bestemmer dimensionerne i praksis.

## 4. Stangkræfter og reaktioner pr. spær

| Lastkombination | Spærhoved ved fod | Spærfod | Trykstiver | Trækdiagonal | Lodret reaktion vest / øst |
|---|---|---|---|---|---|
| K1  1,0 G + 1,5 S(jævn) + 0,75 Q(loft) | -17,4 kN | 15,4 kN | -3,3 kN | 5,8 kN | 9,2 / 9,2 kN |
| K2  1,0 G + 1,5 S(ophobning vest) + 0,75 Q(loft) | -17,9 kN | 15,7 kN | -4,7 kN | 7,3 kN | 9,8 / 6,2 kN |
| K3  0,9 G + 1,5 W(sug) | 2,9 kN | -2,1 kN | 1,6 kN | -0,6 kN | -1,4 / -1,4 kN |

Træk er positivt. Negativ lodret reaktion er løft.

## 5. Vægge, fundamenter og forankring

| | |
|---|---|
| Største lodrette last fra spær | 9,8 kN pr. spær, dvs. 9,8 kN/m væg |
| Antaget egenvægt af ydervæg og sokkel | 8,0 kN/m |
| Linjelast på fundament | ca. 17,8 kN/m |
| Stribefundament 0,6 m bredt | ca. 30 kN/m² på jorden. Jordens bæreevne er ikke undersøgt |
| Største løft fra vind | 1,4 kN pr. spær. Kræver spærbeslag og forankring af remmen ned i væggen |

## 6. Forhold, der skal løses i projekteringen

1. **Bæring på husets gavl.** Langs det eksisterende hus skal spærene hvile på husets vestgavl, som i dag kun bærer sig selv. Gavlens og dens fundaments bæreevne skal vurderes, og der skal laves en rem i tagfodshøjde.
2. **Sammenskæringen med husets tag.** Tilbygningens tag skærer ind i husets tag i to skotrender. De yderste spær i huset skal bære skotrenderne og den sne, der kan samle sig der (DK NA anneks G om tagsammenskæringer).
3. **Springet på 45 cm i østvæggen.** Syd for huset står østvæggen 45 cm længere ude end husets gavl. Spærene i den sydlige del bliver derfor længere, eller tagfoden mod øst kommer lidt lavere. Facadetegningerne viser taget symmetrisk og uden dette spring.
4. **Garageportene i nordgavlen** (to åbninger på 2,7 m) kræver overliggere, og gavlen mister en stor del af sin afstivende skive.
5. **Stabilitet:** tagskive, vindkryds i tagfladen og afstivende vægge er ikke regnet.
6. **Jordvarmeslangen** under den vestlige ydervæg og fundamentets dybde.
7. **Brandadskillelse** mellem garage og bolig, også på loftet.
