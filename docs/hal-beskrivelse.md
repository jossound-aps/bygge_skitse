# Beskrivelse af ny hal, Nældevej 42, 9000 Aalborg

Udarbejdet 10. oktober 2026. Teknisk beskrivelse af hallen og af de regler, konstruktionen skal opfylde for sne- og vindlast.

Beskrivelsen er et grundlag for dialogen med stålleverandør, panelleverandør og den, der skal lave den statiske dokumentation. Den er ikke en statisk beregning. Alle lastværdier i afsnit 4 er vejledende overslag og skal fastlægges af den projekterende.

---

## 1. Hallen kort

| | |
|---|---|
| Ydre mål | 20,0 × 10,0 m, én etage |
| Orientering | Kip nord-syd. Gavle mod nord og syd, tagflader mod øst og vest |
| Sidehøjde | 4,0 m |
| Taghældning | 30° sadeltag |
| Kiphøjde | ca. 6,9 m over soklens overkant (gulv), ca. 7,3 m over terræn. Soklen går 0,4 m over terræn |
| Bærende system | Stålrammer (søjle og spær i ét) på tværs af hallen, som på Grædstrup Ståls referencehal. Antaget rammeafstand ca. 5 m, dvs. fem rammer |
| Tag | Åse i træ på tværs af rammerne, derpå sandwichpaneler, sort |
| Vægge | Vandrette sandwichpaneler, 1 m høje og fire i højden, skruet direkte på rammernes søjler uden rigler. Sort |
| Leverandører | Spær/rammer fra Kaas Staalbyg, paneler fra Panelbyg (FALK 1060 WB til vægge) |
| Åbninger | Én port 4,0 × 4,0 m i nordgavlen mod ridebanen. Gangdør i samme gavl, i siden mod huset. Ingen åbninger i sydgavlen eller langsiderne |
| Indretning | Lukket rum på 40 m² i sydenden. Resten er én åben hal på 160 m² |
| Opvarmning | Ikke afklaret. Forudsat uopvarmet |
| Placering | I den første fold øst for haven, 11,3 m øst for husets østgavl og 11,4 m fra skuret |

Tegninger: [hal_plan.png](../tegninger/hal_plan.png), [hal_indvendig.png](../tegninger/hal_indvendig.png), [isometri.png](../tegninger/isometri.png) og [situationsplan.png](../tegninger/situationsplan.png).

---

## 2. Regelgrundlag for konstruktionen

| Emne | Regel | Betydning for hallen |
|---|---|---|
| Krav til bærende konstruktioner | BR18 kap. 15. Konstruktioner projekteres efter eurocodes med danske nationale annekser | Rammer, åse, paneler, fastgørelser og fundamenter skal alle kunne eftervises |
| Sikkerhed og lastkombinationer | DS/EN 1990 med DK NA | Konsekvensklasse, partialkoefficienter og kombination af sne og vind |
| Snelast | DS/EN 1991-1-3 med DK NA:2024 | Se afsnit 3 og 4 |
| Vindlast | DS/EN 1991-1-4 med DK NA:2024 | Se afsnit 3 og 4 |
| Stål | DS/EN 1993-1-1 med DK NA. Udførelse efter DS/EN 1090-2, CE-mærkning efter EN 1090-1 | Gælder rammerne fra stålleverandøren |
| Træ | DS/EN 1995-1-1 med DK NA | Gælder åsene |
| Sandwichpaneler | EN 14509 (CE-mærkning). Spændvidder og fastgørelse efter producentens tabeller | Gælder væg- og tagpaneler |
| Fundering | DS/EN 1997-1 med DK NA. BR18 § 342: frostsikker dybde og bæredygtig bund | Fundamenter skal også optage løft og vandrette kræfter fra rammerne |
| Dokumentation | BR18 kap. 28: statisk dokumentation (konstruktionsgrundlag, beregninger, tegninger, projektredegørelse) | Skal foreligge senest ved færdigmelding |

De nationale annekser til sne og vind ligger i [kilder/](kilder/). Selve eurocodes er ikke frit tilgængelige; hvor jeg gengiver tal fra dem, er det efter hukommelsen og mærket sådan.

### Konsekvensklasse

DK NA til EN 1990, tabel B1, nævner som eksempler på lav konsekvensklasse (CC1): "1- og 2-etagesbygninger med moderate spændvidder, hvor der kun lejlighedsvis kommer personer, fx lagerbygninger, skure og mindre landbrugsbygninger". Alt andet er middel konsekvensklasse (CC2).

En ren maskinhal kan være CC1. Fordi hallen også skal bruges som værksted med lift, hvor der arbejdes jævnligt, bør den regnes i CC2, medmindre den projekterende vurderer andet. I CC2 er faktoren K_FI = 1,0; i CC1 er den 0,9. Tallene er læst i 2013-udgaven af annekset; den gældende udgave er fra 2024 og bør tjekkes.

---

## 3. Sne- og vindlast: hvad reglerne siger

### 3.1 Snelast (DS/EN 1991-1-3 DK NA:2024)

Snelasten på taget er s = μ · C_e · C_t · s_k, regnet på tagets vandrette projektion.

| Størrelse | Værdi | Kilde |
|---|---|---|
| Terrænværdi s_k | 1,0 kN/m² i hele Danmark | DK NA 4.1(1) |
| Eksponeringsfaktor C_e = C_top · C_s | C_top: 0,8 vindblæst, 1,0 normal, 1,25 afskærmet. C_s = 1,0 for en bygning af denne størrelse | DK NA 5.2(7) |
| Termisk faktor C_t | 1,0 (uopvarmet eller velisoleret tag) | Eurocoden, efter hukommelsen |
| Formfaktor μ1 ved 30° | 0,8 | Eurocodens tabel 5.2, efter hukommelsen |

**Lastarrangementer for et sadeltag:**

| Arrangement | Østlig tagflade | Vestlig tagflade | Kilde |
|---|---|---|---|
| Jævnt fordelt sne | μ = 0,8 | μ = 0,8 | Eurocoden 5.3.3 |
| Omfordelt sne, begge veje | 0,4 / 0,8 | 0,8 / 0,4 | Eurocoden 5.3.3, efter hukommelsen |
| Dansk tillæg: sneophobning på læsiden ved østenvind | 0 | μ_w = 1,2 | DK NA 5.3.3(4) |

**Det danske tillæg er netop relevant for denne hal, fordi kippen ligger nord-syd.** DK NA 5.3.3(4) kræver et ekstra lastarrangement med formfaktor nul på vindsiden og μ_w på læsiden, når alle disse betingelser er opfyldt:

- tagfladen i vindsiden vender mod retninger fra NNØ til SØ (betydende snefygning forekommer kun ved vind fra østlige retninger),
- facadehøjden i vindsiden er højst 10 m,
- to gange kiphøjden er mindre end bygningens udstrækning på tværs af vinden (2 × 6,9 = 13,8 m < 20 m),
- bygningens dybde er større end kiphøjden (10 m > 7,3 m),
- terrænet i vindsiden er åbent i en afstand af 400 m (højst terrænkategori II).

For taghældninger fra 15° til og med 30° er μ_w = 1,2. Over 30° falder den: μ_w = 2,4 − 0,04·α.

De fire første betingelser er opfyldt. Den sidste er tvivlsom: mod øst ligger folde, ridebane og et skovbryn ca. 75 m væk, så terrænet er næppe åbent i 400 m. Det afgør den projekterende; det er på den sikre side at regne tillægget med.

**Om formfaktor 2 og 0,8:** Jeg kan ikke genfinde en formfaktor på 2 for et fritliggende sadeltag i det danske anneks. Den største værdi for denne hal er 1,2 på den vestlige (læ) tagflade, og 0,8 er værdien for jævnt fordelt sne. Formfaktorer op til 2 og derover hører til afsnittet om lægivere (DK NA 5.3.6), dvs. sne, der ophobes op mod en højere bygning, en brystning eller lignende. Det bliver først relevant, hvis der bygges noget højere tæt op ad hallen, eller hvis taget får opbygninger. Spørg den, der har nævnt tallet 2, hvilket punkt i annekset det kommer fra.

Annekset siger desuden, at dimensionering ikke bør forudsætte snerydning, og at der ikke regnes med udhængende sne på tagkanten.

### 3.2 Vindlast (DS/EN 1991-1-4 DK NA:2024)

| Størrelse | Værdi | Kilde |
|---|---|---|
| Basisvindhastighed v_b,0 | 24 m/s i hele Danmark, undtagen en randzone i Jylland under 25 km fra Vesterhavet og Ringkøbing Fjord, hvor den stiger lineært til 27 m/s ved kysten | DK NA 4.2(1)P |
| Retningsfaktor c_dir² | 1,0 for vind fra vest og VNV, ned til 0,6 fra ØNØ og SSØ. Må kun bruges, hvis forudsætningerne består i konstruktionens levetid | DK NA tabel 1a |
| Terrænkategori | Kystnære områder med pålandsvind regnes som kategori I | DK NA 4.3.2(1) |
| Indvendigt vindtryk | Skillevægge kan regnes for en formfaktor på 0,4 | DK NA 7.2.9(6) |

Grunden ligger efter min opmåling på kortet ca. 28 km fra Jammerbugt-kysten, altså lige uden for randzonen, så v_b,0 = 24 m/s. Afstanden er tæt på grænsen, og den projekterende skal selv vurdere det.

**Formfaktorer for udvendigt vindtryk** står i eurocodens afsnit 7.2. Efter hukommelsen er størrelsesordenen for et sadeltag på 30°:

| Flade | Vind på tværs af kippen (øst/vest) | Vind langs kippen (nord/syd) |
|---|---|---|
| Vindside-væg | ca. +0,8 | ca. +0,7 |
| Læside-væg | ca. −0,5 | ca. −0,3 |
| Tagflade i vindsiden | fra −0,5 til +0,7 | sug fra −0,5 til −1,4 i randzonerne |
| Tagflade i læsiden | ca. −0,4 til −0,5 | |
| Indvendigt | +0,2 eller −0,3, når der ikke er en dominerende åbning | |

**Porten er det kritiske punkt for vinden.** Står den 4 × 4 m store port i nordgavlen åben under storm, er den en dominerende åbning, og det indvendige tryk bliver efter eurocoden op mod 75-90 % af det udvendige tryk ved åbningen. Det giver et stort indvendigt overtryk, som lægges oven i suget på taget. Enten skal hallen dimensioneres for åben port, eller også skal det være en forudsætning, at porten er lukket i storm, og porten skal så selv kunne tåle vindlasten.

### 3.3 Lastkombinationer (DS/EN 1990 DK NA)

| Tilfælde | Kombination |
|---|---|
| Sne dominerende | 1,0 · egenvægt + 1,5 · K_FI · sne + 1,5 · K_FI · 0,3 · vind |
| Vind dominerende | 1,0 · egenvægt + 1,5 · K_FI · vind. Sne medregnes ikke (ψ0 = 0 ved dominerende vind) |
| Løft og væltning | 0,9 · egenvægt + 1,5 · K_FI · vind (sug) |
| Kun egenvægt | 1,2 · K_FI · egenvægt |

Faktorerne er fra DK NA tabel A1.1 og A1.2(B+C), læst i 2013-udgaven.

---

## 4. Vejledende lastværdier for hallen

Overslag for at give en størrelsesorden. De er ikke en beregning.

### 4.1 Sne

Med s_k = 1,0, C_e = 1,0 (normal topografi) og C_t = 1,0:

| Arrangement | Karakteristisk last | Pr. ramme ved 5 m rammeafstand |
|---|---|---|
| Jævnt fordelt | 0,8 kN/m² på begge tagflader | 4,0 kN/m |
| Omfordelt | 0,4 og 0,8 kN/m² | 2,0 og 4,0 kN/m |
| Ophobning på vestlig tagflade | 0 mod øst, 1,2 kN/m² mod vest | 0 og 6,0 kN/m |

Regningsmæssigt (× 1,5) svarer det til 1,2 kN/m² for jævn sne og 1,8 kN/m² for ophobningen på den vestlige tagflade. 1,2 kN/m² svarer til ca. 60 cm sne.

Er hallen omgivet af høje træer, kan topografien være "afskærmet" med C_top = 1,25, og så stiger alle værdier med 25 %. Læbæltet mod vest og skovbrynet mod øst er omtrent lige så høje som hallen, så det bør vurderes.

### 4.2 Vind

Med v_b,0 = 24 m/s er basishastighedstrykket 0,36 kN/m². Spidshastighedstrykket i kiphøjde 6,9 m har jeg regnet til:

| Terrænkategori | q_p |
|---|---|
| II (åbent landbrugsland) | ca. 0,76 kN/m² |
| III (læbælter, spredt bebyggelse) | ca. 0,53 kN/m² |

Med kategori II på den sikre side giver det i størrelsesorden:

- **Vægge:** tryk ca. 0,6 kN/m² på vindsiden og sug ca. 0,4 kN/m² på læsiden, plus indvendigt tryk eller sug på op til ca. 0,2 kN/m².
- **Tag:** sug på ca. 0,4-0,6 kN/m² over det meste af fladen, op til ca. 1,1 kN/m² i hjørner og langs kanter ved vind langs kippen.
- **Åben port:** indvendigt overtryk i størrelsesordenen 0,5 kN/m², som lægges til suget på taget.

### 4.3 Hvad det betyder

- **Sne er dimensionerende for spær og søjler nedad.** Den vestlige tagflade skal kunne bære ophobningen (1,2), hvis det danske tillæg gælder.
- **Vind er dimensionerende for løft.** En let stålhal vejer omkring 0,3 kN/m², og suget er større end det. Hver søjle skal derfor forankres i et fundament, der kan holde igen mod løft, i størrelsesordenen 15-25 kN pr. søjle, mere ved åben port.
- **Vind på gavlene** (hver gavl er ca. 55 m²) skal føres ned gennem hallens længderetning. Rammerne er kun stive på tværs.

---

## 5. Konstruktive forhold, der skal afklares med leverandørerne

1. **Afstivning i længderetningen.** Rammerne optager vind på langsiderne. Vind på gavlene kræver vindkryds eller anden afstivning i tag og vægge i mindst ét fag i hver side, medmindre panelernes skivevirkning er dokumenteret. Når vægpanelerne skrues direkte på søjlerne uden rigler, er der ikke andet til at fordele kræfterne, så det skal stålleverandøren tage stilling til.
2. **Vægpanelernes spændvidde.** Uden rigler spænder panelerne fra ramme til ramme. Efter FALK's tabel (hollandske vindlaster) klarer 1060 WB ca. 3,8 m ved 60 mm, 4,4 m ved 80 mm, 4,9 m ved 100 mm og 5,5 m ved 120 mm. Med 5 m rammeafstand kræver det altså ca. 120 mm, eller tættere rammer. Skal regnes efter danske vindlaster.
3. **Panelernes mål.** FALK 1060 WB har 1,06 m dækbredde. Fire paneler giver 4,24 m, ikke 4,0 m.
4. **Gavlene.** Gavlrammerne skal have gavlstolper til at bære panelerne og portåbningen. Porten på 4 × 4 m skal have en overligger og sidestolper, der kan optage vindlasten fra portbladet.
5. **Åse og tagpaneler.** Åsenes afstand bestemmes af tagpanelets spændvidde og af sne- og suglasten. Fastgørelsen af åse til spær og af paneler til åse skal dimensioneres for sug, især i randzonerne.
6. **Fundamenter.** Hallen funderes på en gennemgående sokkel hele vejen rundt, ikke punktfundamenter. Soklen skal under søjlerne optage tryk fra sne, løft fra vind og den vandrette kraft fra rammens fod. Frostsikker dybde er normalt 0,9 m; for uopvarmede bygninger bruges ofte 1,2 m (min hukommelse, tjek med den projekterende). Den nye placering øst for haven ligger fri af jordvarmeslangerne.
7. **Åben eller lukket port.** Se afsnit 3.2. Det skal fremgå af konstruktionsgrundlaget.
8. **Ét samlet ansvar.** Rammer, paneler og fundament kommer fra forskellige leverandører. Den statiske dokumentation skal dække hele bygningen, også samlingerne mellem leverancerne og den samlede stabilitet. Aftal, hvem der står for den.
9. **Brand.** Om stålrammerne skal have brandmodstand (R15), afhænger af, om hallen behandles som driftsbygning eller som garage/udhus. Se [regelrapport.md](regelrapport.md) afsnit 8.6.

---

## 6. Dokumentation til byggesagen

Hallen forventes at kunne placeres i konstruktionsklasse 1 (én etage, spændvidde under 40 m, simple og traditionelle konstruktioner), så der kræves ikke certificeret statiker. Ved ansøgning skal grundlaget for indplaceringen oplyses. Ved færdigmelding skal den statiske dokumentation foreligge, i relevant omfang:

- A1 Konstruktionsgrundlag: laster (herunder sne- og vindforudsætningerne ovenfor), konsekvensklasse, materialer, funderingsforhold.
- A2 Statiske beregninger: rammer, åse, paneler og fastgørelser, afstivning, fundamenter.
- A3 Konstruktionstegninger.
- B1 Statisk projektredegørelse.

Stålleverandøren oplyser, at dokumentation efter gældende normer følger med deres leverance. Det dækker rammerne, men ikke nødvendigvis paneler, fundament og samlet stabilitet.

---

## 7. Spørgsmål til leverandørerne

**Kaas Staalbyg**

- Hvilken rammeafstand og hvilke profiler foreslår I til 10 m spændvidde, 4 m sidehøjde og 30° taghældning?
- Regner I med det danske lastarrangement for sneophobning (μ_w = 1,2 på vestlig tagflade), og med åben eller lukket port?
- Hvordan afstives hallen i længderetningen, når vægpanelerne monteres direkte på søjlerne?
- Hvilke reaktioner (tryk, løft, vandret) skal fundamenterne dimensioneres for?
- Kan rammerne dokumenteres som R15 uden brandmaling?

**Panelbyg**

- Hvilken tykkelse af FALK 1060 WB kræves for at spænde fra ramme til ramme ved danske vindlaster?
- Hvilket tagpanel anbefales, og hvilken åseafstand kræver det?
- Kan panelerne dokumenteres som K1 10/B-s1,d0 (vægge) og B_ROOF(t2) (tag)?

## 8. Tagvand: tilslutning til ridebanens afløb og pumpe (vurdering 10.10.2026)

Ejer har besluttet, at tagvandet kobles på de afløb, der allerede ligger ved ridebanen og fører til en pumpe, som pumper vandet væk. Det er en bedre løsning end faskiner her, fordi den ikke afhænger af grundvandsstanden. Vurderingen er et overslag; pumpen og ledningerne er ikke set.

### Mængder

| Størrelse | Værdi |
|---|---|
| Tagflade i plan, med udhæng | ca. 210 m², 105 m² til hver side |
| Største tilløb fra taget ved kraftig byge (5-10-års regn, 10 minutter) | ca. 4-5 l/s |
| Vand fra et døgn med 40 mm regn | ca. 8,5 m³ |
| Ridebanen til sammenligning | ca. 780 m², men vandet siver langsomt gennem sand og bundlag |

Taget øger det areal, pumpen betjener, med godt en fjerdedel. Tagvandet kommer til gengæld på få minutter, hvor ridebanens vand kommer over timer. Det er spidsen på 4-5 l/s, pumpen eller brønden skal kunne tage.

### Pumpen og drænet (ejers oplysninger 10.10.2026)

- Pumpen yder ca. 200 l/min, dvs. 3,3 l/s.
- Der ligger afløb under hele ridebanen og hele vejen rundt om den.
- Pumpen står i ridebanens hjørne mod vejen og øst.

Pumpen kan altså ikke alene tage spidsen fra taget (4-5 l/s), og den skal samtidig tage ridebanens eget vand. Over et døgn er der rigelig kapacitet: pumpen flytter 288 m³ i døgnet, og tag og ridebane giver tilsammen ca. 40 m³ ved 40 mm regn. Problemet er kun de første 10-30 minutter af en kraftig byge.

| Byge (ca. 5-års regn) | Fra taget | Pumpen kan nå, hvis halvdelen af ydelsen er fri | Skal gemmes |
|---|---|---|---|
| 10 minutter, ca. 13 mm | 2,7 m³ | 1,0 m³ | ca. 1,7 m³ |
| 30 minutter, ca. 19 mm | 4,0 m³ | 3,0 m³ | ca. 1,0 m³ |
| 60 minutter, ca. 23 mm | 4,8 m³ | 6,0 m³ | 0 |

Regntallene er runde værdier, ikke kommunens dimensioneringsregn.

### Anbefalet løsning

1. **Forsinkelsesbrønd eller tank på ca. 3 m³** mellem hallen og ridebanen, med et droslet udløb på ca. 1 l/s. Så mærker pumpen næsten ikke taget, og ridebanen bliver ikke vådere end i dag.
2. **Tilslut til omfangsdrænet ved ridebanens sydkant**, som ligger få meter fra hallens nordgavl. Tilslut i en brønd på samleledningen, ikke direkte i de slidsede rør under banen, så tagvandet ikke siver ud i bundlaget.
3. **Sandfang og bladfang** på nedløbene.
4. **Overløb fra forsinkelsesbrønden** ud på terræn væk fra hallen, til pumpestop og strømsvigt. En niveaualarm på pumpen er billig.
5. **Ledning** Ø110 mm med mindst 10 ‰ fald. Den krydser kørevejen foran porten og skal tåle trafik dér.

Uden forsinkelse vil en kraftig byge stuve op i omfangsdrænet og bundlaget, til pumpen har indhentet det. Det skader ikke hallen, men ridebanen bliver våd i nogle timer.

### Tilladelse

Det afhænger af, hvor pumpen sender vandet hen. Pumper den til grøft, vandløb eller sø, er det en udledning efter miljøbeskyttelseslovens § 28, og mere vand end i dag kan kræve, at kommunen godkender ændringen. Det er uvist, om den nuværende udledning fra ridebanen har en tilladelse. Kommunen krævede særskilt tilladelse til tagvand i sag S2025-10959, så vi skal regne med at blive spurgt.

### Mangler

- Hvor pumpen leder vandet hen (afgør, om der skal søges udledningstilladelse).
- Om omfangsdrænet har en brønd ved sydkanten, der kan tilsluttes i.
