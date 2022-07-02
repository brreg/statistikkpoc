# Forsøk: Erstatte spørreskjema fra SSB med spørring mot bokføringsdata i form av SAF-T-filer

## Formål
I [Nordic Smart Government and Business](https://nordicsmartgovernment.org) jobber vi med "Open Accounting and Simplified
Reporting". Innenfor dette løsningsområdet tester vi ut om en av SSBs spørreundersøkelser,
Varehandelsindeksen, som idag er et Altinn-spørreskjema, kan erstattes med å hente de relevante opplysningene
direkte fra bedriftens bokføringssystem, gjennom en såkalt SAF-T-fil.

Spørsmål? Kontakt Steinar Skagemo - stsk@brreg.no

## Potensialet i bredere bruk av SAF-T
SAF-T Financial standarden er et obligatorisk format for levering av
bokføringsdata fra digitale bokføringsprogram, og kravet gjelder for alle bokføringsperioder
som starter etter 1. januar 2020. Kravet er hjemlet i bokføringsloven og -forskriften. En av de viktigste
begrunnelsene for å innføre kravet var skattemyndighetenes behov for innsyn i bokføringen for kontrollformål.
Det var samtidig klart at formatet vil kunne ha verdi for mange formål utover dette, og det fremgår også Skatteetatens
[dokumentasjonen av standarden](https://www.skatteetaten.no/globalassets/bedrift-og-organisasjon/starte-og-drive/rutiner-regnskap-og-kassasystem/saf-t-regnskap/oppdateringer/norwegian-saf-t-financial-data---documentation.pdf):

> The primary purpose of the SAF-T Financial data format is to:
- Serve as an export format for accounting data after request from the
NorwegianTax Administration, public accountants and other parties.
- Serve as archiving format for the necessary accounting data for those who are
obliged to keep accounts as stated in the Norwegian bookkeeping legislation.
- Serve as a format for moving data when changing accounting software.
- Serve as a format for moving data from accounting software to other financial
systems such as year-end closing systems, tax computation systems, business
intelligence software, advisory systems etc.

SSB har sett nærmere på hvilke muligheter som ligger for å forenkle rapporteringen til SSB gjennom å utnytte SAF-T-filene. Deres konklusjon er at en stor andel av de opplysningene
SSB ber næringslivet om i sine spørreundersøkelser, kan hentes ut fra dataene i en SAF-T-fil. Det vil kunne forenkle
prosessen for de næringsdrivende som blir bedt om å fylle ut opplysningene, og samtidig gi bedre datakvalitet for
SSB.

I arbeidet har vi (SSB og Brønnøysundregistrene) hatt dialog med Skatteetaten, Regnskap Norge og Amesto om verdien og
gjennomførbarheten. En felles oppfatning er at innføringen av kravet til SAF-T har skapt et stort potensiale for
forenklinger og forbedringer i alle prosessene der en er avhengig av bokføringsdata, eller av informasjon som kan
utledes av bokføringsdata. Vi er derfor opptatt av at den metodikken vi tester ut i forsøket skal kunne brukes
også i andre sammenhenger, og ikke bare av SSB.

Et grunnleggende spørsmål er hvem som skal ha tilgang til bokføringsdataene, for å kunne hente ut de relevante
opplysningene. En hypotese er at SSB skal kunne få svar på sitt behov for informmasjon, uten selv å motta den
detaljerte bokføringen i form av den komplette SAF-T-filen, men isteden kunne formulere en maskinlesbar spørring
inn mot filen, og få resultatene i retur.

I skjermbildet nedenfor er det angitt at det er ønskelig med sum for transaksjonene som er bokført på 3000-kontoene (salg) og som er bilagsført i januar 2017, og nederst i bildet er svaret fra API-et:
![Skjermbilde av forespørsel til og svar fra API-et](demo-snapshot.png)

*Disclaimer*: Ikke se her for å lære beste praksis Python-koding ... Arbeidet følger rådet om å jobbe etter rekkefølgen
"make it work, make it right, make it fast", og alt fokus er foreløpig på det første steget ...

## Uavklarte spørsmål
- Varehandelsindeksen er et månedlig spørreskjema, mens det er sannsynlig at bokføringen av mange innrettes for å møte
MVA-rapporteringsfristen, som er annenhver måned
- Varehandelsindeksen ber om at de relevante tallene er brutt ned på underenheter, finnes det tilstrekkelig fast
praksis for hvordan dette bokføres og representeres i SAF-T-filen?
- Grensesnittet for sluttbrukeren (bedriften) som blir bedt om å svare på spørreundersøkelsen: Hvordan bør bedriften
presenteres for oppgaven å levere tall til spørreundersøkelsen, valget om å hente disse automatisk og godkjenning
av at tallene rapporteres til SSB?
- Hvor generisk kan API-et være for å dekke flere formål, og samtidig gi bedriften trygghet for at de ikke blir lurt
til å deler detaljert bokføringsinformasjon som avslører forretningshemmeligheter?
- SAF-T-standarden er standarden for bokføringsinformasjonen, men bør det i tillegg benyttes en standard for resultatet
av forespørselen, f.eks. en standard for finansiell rapportering som XBRL / iXBRL?

## Foreløpig løsning
Den foreløpige løsningen består av følgende komponenter:

1) API - oa_api.py
2) Analyse - analyse.py
3) Konvertering av SAF-T til Pandas DataFrame - saft2dataframe.py

### Om 1 - API - oa_api.py
Dette er grensesnittet som SSB kan bruke til å sende en forespørsel der de formulerer for hvilken tidsperiode 
og hvilke kontoer de ønsker resultatet fra. 

Merk at vi i forsøket ikke har lagt inn noen mekanismer for autentisering/autorisering i API-et, men det er en
forutsetning for en reell implementering. Det skal *ikke* lages et API som gir hvem som helst tilgang til å gjøre
spørringer mot bokføringsdataene til et hvilket som helst selskap i Norge.


API-et støtter GET, og presisering av datointervall og et intervall av kontoer i henhold til [standardkontoene](https://github.com/Skatteetaten/saf-t/tree/master/General%20Ledger%20Standard%20Accounts) i SAF-T:

```
GET /orgnr/888888888?from_and_included_date=2017-01-01&to_date=2017-02-01&from_and_included_account_id=3000&to_account_id=4000 HTTP/1.1
```

Resultatet er en JSON som viser summene for disse kontoene, i det angitte tidsintervallet, for de tre beløpsfeltene
som er relevante for varehandelsindeksen:

```
HTTP/1.1 200 OK
content-length: 100
content-type: application/json
date: Fri, 01 Jul 2022 17:14:41 GMT
server: uvicorn

{
    "Line.CreditAmount.Amount": 717838.0,
    "Line.DebitAmount.Amount": 0.0,
    "Line.TaxAmount.Amount": 179458.0
}
```
TODO: Gjenstår å få verifisert at det er riktige felt som er summert!

Modulen mottar query-parametrene i GET-forespørselen og sender dem videre
som parametre til analyse-funksjonen i analyse.py, og får tilbake resultatet av analysen.

### Om 2 - Analyse - analyse.py
Dette er modulen som gjennomfører analysen. Den får den relevante SAF-T-filen som en pandas DataFrame fra modulen
saft2dataframe, og filtrerer og summerer dataene i henhold til parametrene den har mottatt fra API-et. Resultatet
av analysen returneres til API-et som deretter kan sende det tilbake til den som sendte forespørselen.

```
return dict(df.loc[
        (                                                         # filtering transactions:
            df['Transaction.TransactionDate'] >= from_and_included_date)     # from 
            & (df['Transaction.TransactionDate'] < to_date)   # ... to (but not included) 
            & (df['Line.AccountID'] >= from_and_included_account_id) # including the accounts
            & (df['Line.AccountID'] < to_account_id)] \
            [[  
            'Line.DebitAmount.Amount',  # selecting the relevant amount-columns
            'Line.TaxAmount.Amount',
            'Line.CreditAmount.Amount',]].sum()) # and summing those
```

### Om 3 - SAF-T til pandas DataFrame - saft2dataframe.py
Denne mottar navn og bane til en SAF-T-fil, og konverterer innholdet til en pandas DataFrame, som returneres.
Det er kun den delen av filen som inneholder data om de bokførte transaksjonene (<Transaction>-elementene) som 
hentes ut. Foreløpig ignoreres <Analysis>-elementene, som brukes til å registrere dimensjoner som avdeling og 
prosjekt på transaksjonene.

## Teknisk informasjon
Dette prosjektet er laget i Python, versjon 3.10. Det er ikke brukt noen spesielle funksjoner fra de aller nyeste
python-versjonene så antagelig vil det fungere på eldre versjoner, men det er ikke testet.

analyse.py og saft2dataframe forutsetter pandas.

oa_api.py forutsetter [FastAPI](https://fastapi.tiangolo.com). Kjør API-et med kommandoen ```uvicorn oa_api:app --reload``` (stå i katalogen ```src```). Swagger-UI-dokumentasjon av API-et, som også kan brukes til å sende forespørsler til det, finner du på ```[serveradressen]/docs```

![Illustrasjon fra API-dokumentasjonen](SwaggerUI-example.png)

## Referanser
- [Skatteetatens dokumentasjon av SAF-T](https://www.skatteetaten.no/globalassets/bedrift-og-organisasjon/starte-og-drive/rutiner-regnskap-og-kassasystem/saf-t-regnskap/oppdateringer/norwegian-saf-t-financial-data---documentation.pdf)
- [Teknisk SAF-T-dokumentasjon, inkludert eksempelfilen dette prosjektet bygger på](https://github.com/Skatteetaten/saf-t)
- [Nordic Smart Government and Business - Open Accounting and Simplified Reporting](https://nordicsmartgovernment.org/open-accounting)
- [Varehandelsindeksen SSB](https://www.ssb.no/varehandel-og-tjenesteyting/varehandel/statistikk/varehandelsindeksen)
- [Varehandelsindeksen - Altinn](https://www.altinn.no/skjemaoversikt/statistisk-sentralbyra/manedlig-omsetning-for-detaljhandel/)
- [Tidligere arbeid med referanseimplementasjon av API i NSG&B](https://github.com/nordicsmartgovernment/nordicsmartgovernment)