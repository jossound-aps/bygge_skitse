# Foreløbig overslagsberegning for hallens bærende konstruktion

Nældevej 42, 9000 Aalborg. 11. oktober 2026. Hører til tegningerne A1.2-A1.4.

**Beregningen er foreløbig.** Den er udført af bygherren som grundlag for landzoneansøgningen og for dialogen med producenten, og den viser, at den ansøgte bygning kan udføres med sædvanlige dimensioner. Den endelige statiske dokumentation udarbejdes af producenten af stålrammerne (Kaas Staalbyg) og vedlægges byggeansøgningen; den kan give andre profiler og dimensioner.

Beregningen følger DS/EN 1990, DS/EN 1991-1-3 og DS/EN 1991-1-4 med de danske nationale annekser (DK NA 2024 for sne og vind), DS/EN 1993-1-1 og DS/EN 1995-1-1. Rammen er regnet som plan, elastisk rammekonstruktion med stive hjørner (elementmetode, 16 elementer pr. stang), og lastkombinationerne er dannet efter DS/EN 1990 DK NA, ligning 6.10a/b.

## 1. Forudsætninger

| | |
|---|---|
| Geometri | Spændvidde 10,0 m, sidehøjde 4,0 m og kiphøjde 6,89 m over soklens overkant (gulv), taghældning 30°. Soklen går 0,4 m over terræn, så kippen er 7,29 m over terræn |
| System | To-charniers stålramme (leddelt ved fundament, stive rammehjørner og kip), samme profil i søjler og spær |
| Rammeafstand | 5,0 m (fem rammer). Beregnet for en mellemramme |
| Stål | S235, f_y = 235 MPa, γ_M0 = 1,1, γ_M1 = 1,2 |
| Konsekvensklasse | CC2, K_FI = 1,0 |
| Egenlast | Tag 0,25 kN/m² (paneler, åse, beslag), vægge 0,15 kN/m², plus rammens egenvægt |
| Sne | s_k = 1,0 kN/m², C_e = C_t = 1,0. Jævn μ = 0,8; omfordelt 0,8/0,4; ophobning på vestlig tagflade μ_w = 1,2 (DK NA 5.3.3(4)) |
| Vind | q_p = 0,78 kN/m² (v_b = 24 m/s, terrænkategori II, z = 7,3 m) |
| Lastkombinationer | DS/EN 1990 DK NA, tabel A1.2(B): γ_G = 1,0 (1,2 når egenlast er dominerende), γ_Q = 1,5, K_FI = 1,0 (CC2). ψ0 = 0,3 for vind sammen med dominerende sne; ψ0 = 0 for sne sammen med dominerende vind (DK NA tabel A1.1) |

Sneophobningen efter DK NA 5.3.3(4) gælder, når tagfladen i vindsiden vender mod NNØ til SØ (vores østlige tagflade), facadehøjden i vindsiden er højst 10 m, 2h < l (2 × 7,3 = 14,6 m < 20 m), b > h (10 m > 7,3 m) og terrænet i vindsiden er åbent (terrænkategori II) i 400 m. Den sidste betingelse er næppe opfyldt, fordi skovbrynet ligger ca. 35 m øst for hallen; lastarrangementet er alligevel medtaget på den sikre side. Formfaktoren 2,0 i DK NA gælder kun ophobning ved højere bygværker (5.3.6) og på altaner (anneks H), ikke et fritliggende sadeltag.

Formfaktorer for vind (c_pe − c_pi), aflæst af DS/EN 1991-1-4 tabel 7.1 (vægge, h/d = 0,73) og tabel 7.4a (sadeltag 30°) og forenklet til én værdi pr. stang; randzonerne F, G og A er ikke medtaget for rammen. Indvendigt tryk c_pi = +0,2 eller −0,3:

| Tilfælde | Søjle vest | Tag vest | Tag øst | Søjle øst |
|---|---|---|---|---|
| W1 | 1,1 | 0,7 | 0,3 | -0,2 |
| W1e | -0,2 | 0,3 | 0,7 | 1,1 |
| W2 | 0,6 | -0,5 | -0,7 | -0,7 |
| W3 | -1,0 | -1,0 | -1,0 | -1,0 |

W1: vind fra vest med tryk på vindsidens tag og indvendigt sug. W1e: samme fra øst. W2: vind fra vest med sug på taget og indvendigt overtryk. W3: vind langs kippen med sug på hele rammen og indvendigt overtryk. Positiv værdi er tryk ind mod bygningen. Åben port i storm er ikke regnet med. v_b,0 = 24 m/s, fordi hallen ligger ca. 28 km fra Vesterhavet (DK NA 4.2(1)P: 27 m/s kun inden for 25 km); terrænkategori II, c_r(7,3 m) = 0,95, I_v = 0,20, q_p = 0,78 kN/m².

## 2. Valg af rammeprofil

Krav: udnyttelse højst 1,0, nedbøjning i kip for karakteristisk sne højst L/200 = 50 mm, og vandret udbøjning i tagfod for karakteristisk vind højst h/150 = 27 mm.

| Profil | kg/m | Tværsnit | Søjle (knæk i rammens plan) | Spær | Nedbøjning kip | Udbøjning tagfod | Opfylder |
|---|---|---|---|---|---|---|---|
| IPE 200 | 22,4 | 1,37 | 1,57 | 1,57 | 28 mm | 108 mm | nej |
| IPE 220 | 26,2 | 1,07 | 1,22 | 1,22 | 20 mm | 75 mm | nej |
| IPE 240 | 30,7 | 0,84 | 0,95 | 0,95 | 14 mm | 54 mm | nej |
| IPE 270 | 36,1 | 0,64 | 0,72 | 0,72 | 10 mm | 36 mm | nej |
| IPE 300 | 42,2 | 0,50 | 0,56 | 0,56 | 7 mm | 25 mm | ja |
| IPE 330 | 49,1 | 0,40 | 0,44 | 0,44 | 5 mm | 18 mm | ja |
| IPE 360 | 57,1 | 0,32 | 0,35 | 0,35 | 3 mm | 13 mm | ja |

**Mindste profil, der opfylder kravene i dette overslag: IPE 300.** Stålvægt for fem rammer: ca. 4124 kg.

Udnyttelserne er regnet som N/N_Rd + M/M_Rd med plastisk bøjningsmodstand (tværsnitsklasse 1). Søjlens knæklængde i rammens plan er sat til 2,46 × søjlehøjden efter en tilnærmet formel for to-charniers rammer med stive hjørner, og spærets til 2 × spærlængden; søjlereduktionen χ er regnet efter DS/EN 1993-1-1, 6.3.1 med knækkurve a (α = 0,21). Producenten efterviser knæklængderne i sit eget beregningsprogram.

**Ikke eftervist:** kipning af spær og søjler, samlinger (rammehjørne, kip, fodplade), knæk ud af rammens plan, lokale forhold ved porten og gavlrammerne. Kipning kræver, at den trykkede inderflange ved rammehjørnet fastholdes, f.eks. med skråstivere fra åsene. Disse forhold kan øge profilet eller kræve udfligning af rammehjørnet, som på referencehallen.

## 3. Snitkræfter og reaktioner for IPE 300

| Lastkombination | M rammehjørne | M kip | N søjle | Lodret reaktion vest / øst | Vandret reaktion |
|---|---|---|---|---|---|
| K1  1,0 G + 1,5 S(jævn) + 0,45 W(tryk) | 34,5 kNm | 19,7 kNm | -46,5 kN | 46,6 / 50,7 kN | 15,9 kN |
| K2  1,0 G + 1,5 S(ophobning vest) + 0,45 W(fra øst) | 52,3 kNm | 15,6 kNm | -54,3 kN | 54,5 / 27,8 kN | 13,8 kN |
| K3  1,0 G + 1,5 S(omfordelt) + 0,45 W(tryk) | 26,0 kNm | 15,6 kNm | -42,7 kN | 42,8 / 39,5 kN | 13,8 kN |
| K4  1,0 G + 1,5 W(tryk) | 24,1 kNm | 1,0 kNm | -21,9 kN | 22,1 / 35,7 kN | 18,9 kN |
| K5  0,9 G + 1,5 W(sug, på tværs) | 43,2 kNm | 4,5 kNm | 15,2 kN | -11,2 / 1,7 kN | 17,8 kN |
| K6  0,9 G + 1,5 W(sug, langs kip) | 7,0 kNm | 18,7 kNm | 20,5 kN | -16,4 / -16,4 kN | 10,0 kN |
| K7  1,2 G | 13,1 kNm | 6,3 kNm | -16,9 kN | 17,1 / 17,1 kN | 3,3 kN |

Normalkraft: træk er positivt. Lodret reaktion: positiv er tryk på fundamentet, negativ er løft.

## 4. Åse

Konstruktionstræ C24, 5 åse pr. tagflade med ca. 1,2 m afstand langs spæret. Regnet som simpelt understøttede for ophobet sne (μ = 1,2) vinkelret på taget; lasten langs taget forudsættes optaget af tagpanelerne. k_mod = 0,9, γ_M = 1,35.

| Dimension | Spænd 5,0 m: udnyttelse | nedbøjning (krav 25 mm) | Spænd 4,0 m: udnyttelse | nedbøjning (krav 20 mm) |
|---|---|---|---|---|
| 45 × 195 mm | 1,29 | 29 mm | 0,82 | 12 mm |
| 45 × 220 mm | 1,01 | 20 mm | 0,65 | 8 mm |
| 45 × 245 mm | 0,82 | 14 mm | 0,52 | 6 mm |
| 70 × 220 mm | 0,65 | 13 mm | 0,42 | 5 mm |
| 75 × 225 mm | 0,58 | 11 mm | 0,37 | 5 mm |
| 95 × 220 mm | 0,48 | 9 mm | 0,31 | 4 mm |
| 95 × 245 mm | 0,39 | 7 mm | 0,25 | 3 mm |

Med 5 m mellem rammerne kræves ca. **45 × 245 mm**. Det er kraftige åse; med 4 m rammeafstand (seks rammer) kan de blive mindre. Stålåse (Z- eller C-profiler) er et almindeligt alternativ ved 5 m. Tagpanelets tilladte spændvidde bestemmer den endelige åseafstand.

## 5. Fundamenter

| | |
|---|---|
| Største lodrette tryk fra rammen | 54,5 kN (regningsmæssigt) |
| Største løft fra rammen | 16,4 kN |
| Tillæg til løft i afstivede fag (vægkryds) | 12,7 kN |
| Største vandrette kraft i rammefod | 18,9 kN |
| Fundament | Gennemgående armeret betonsokkel hele vejen rundt, 0,40 m bred, 0,9 m under terræn og 0,4 m over. Ingen punktfundamenter |
| Soklens egenvægt | 12,5 kN/m |
| Kontrol af løft | 3,0 m sokkel regnes aktiveret ved hver rammefod: 0,9 × 37,4 = 33,7 kN mod 29,2 kN: opfyldt |
| Tryk på jorden under en rammefod | ca. 78 kN/m², når lasten spredes over 2,9 m sokkel. Jordens bæreevne er ikke undersøgt |

Soklens underside ligger i 0,9 m dybde som forudsat frostsikker; for uopvarmede bygninger kan der kræves større dybde. Den vandrette kraft i rammefoden skal optages af fundamentet (jordtryk og friktion) eller af et trækbånd i gulvet mellem modstående fundamenter. Løftet forudsætter, at soklen er armeret i længderetningen, så den kan fordele kræfterne fra rammefoden, og at søjlens fodplade er forankret i soklen. Soklen bærer også vægpanelerne.

## 6. Afstivning i længderetningen

Rammerne er kun stive på tværs. Vind på gavlene føres via et vindgitter i tagfladen til vægkryds i langsiderne.

| | |
|---|---|
| Gavlareal | 54,4 m² |
| Regningsmæssig kraft til tagets vindgitter fra én gavl | 31,8 kN |
| Kraft pr. langside | 15,9 kN |
| Træk i vægdiagonal (fag 5,0 × 4,0 m) | 20,4 kN |
| Rundstål Ø16 S235, bæreevne ca. 157 mm² × 235 / 1,1 | 33,5 kN: tilstrækkeligt |

Der er tegnet krydsafstivning i ét fag i hver langside og i tagfladen i samme fag. Når vægpanelerne skrues direkte på søjlerne uden rigler, findes der ingen andre dele, der kan overføre kræfterne, så krydsene er nødvendige, medmindre leverandøren dokumenterer panelernes skivevirkning.

## 7. Det skal den projekterende tage stilling til

1. Rammeafstand: 5 m giver kraftige åse og kræver ca. 120 mm vægpanel; 4 m letter begge dele.
2. Kipning og samlinger, som ikke er eftervist her.
3. Om det danske lastarrangement for sneophobning gælder (terrænet 400 m mod øst er ikke åbent på grund af skovbrynet); her er det medtaget på den sikre side.
4. Åben eller lukket port i storm.
5. Gavlrammerne: stolper og overligger ved porten (4,0 × 4,0 m) og fastgørelse af gavlpanelerne.
6. Jordbundsforhold og funderingsdybde.
7. Konsekvensklasse (CC2 er forudsat).
