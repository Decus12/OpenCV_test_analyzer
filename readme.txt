OPITTUA:

Opin uusia tapoja käsitellä kuvaa esimerkiksi kontrastia ja sen soveltamista hyväksikäyttäen.
Algoritmin skaalautuminen mahdollisimman paljon kuvan koon tai niiden määrien mukaan oli jatkuvasti
asia, jonka kautta pyrin koodaamaan tapauskohtaisen kovakoodauksen sijaan. Jossain määrin opin myös,
missä määrin käyttäjävirhettä voidaan ehkäistä suunnittelulla. Tärkeimpänä projektissa tuli vastaan
tilanteita, joihin ei ollut helppoa ja suoraviivaista ratkaisua joko valmiina tai jo tehtyä koodia
muokkaamalla. Niinpä ongelmanratkontaa täytyi harrastaa paljon ja kehittää jo olemassa olevien
metodien rinnalle uusia toimintoja, jotka joko avustivat erottamaan ei-halutut tulokset halutuista tai
paransivat tuloksia poistamalla hajontaa, mutta kuitenkin siten että alkuperäisestä kuvasta saatiin
yhä lopputulokset laskettua.  

ONGELMIA:
Ihmeellisten haamubugien (ratios muuttuja muuttaa arvojaan kesken loopin) lisäksi mitään kovin suuria
ongelmia ei ollut. Enimmät liittyvät lopulta template matchingiin, jonka kanssa täytyy olla tarkka
siitä millaisen templaten laittaa. Ensinnäkin template kuvan koolla on väliä, joten sen kanssa olisi
hyvä lopulta käyttää myöskin skaalausta. Toisekseen rarkaisevaa on, mitä template kuvassa on. Liian
paljon vaikeuttaa tulosten laskentaa, mutta liian niukasti informaatiota johtaa myös helposti täysin
päättömiin mukaparhaisiin tuloksiin. Niinpä sitä täytyy avustaa esimerkiksi rajoittamalla mille
alueelle kuvassa sitä käytetään ja antamalla template kuvaan jotain selkeitä ja voimakkaita piirteitä,
sillä pelkät varjostukset eivät siinä lopulta paljoa paina.

MITEN TOIMII:

Classifier_teach.py:

Opetusalgoritmi ajaa usean kuvan analyysialgoritmin (multi_img.py) ja lukee sen exceliin
kirjoittamista tuloksista referenssinumerot ja T/C-ratiot. Tämän jälkeen se laskee kuinka monta kuvaa
kussakin referenssiluokassa oli siltä varalta, että niitä ei ole kaikki yhtä suuri määrä. Käyttäen
kunkin refenrenssiluokan määrää käydään niiden ratiot läpi ja lasketaan ration keskiarvo ja standard
deviation. Niiden jälkeen lasketaan mitkä luokat olisi syytä yhdistää. Ehdot ovat, että kaksi luokkaa
ovat keskiarvoltaa tismalleen samanlaiset (=kumpikin ovat keskiarvoltaan 0) tai että kahden luokan
keskiarvon puoliväli on alemman tason luokan SD:tä lähempänä. 

Luokkia yhdistetään korkeintaan 2 kerrallaan, sillä muuten yhdistyksestä saattaisi seurata
ketjureaktio, jossa useita luokkia ketjuuntuisi yhdeksi massiiviseksi luokaksi. Koska jo kahden
luokan yhdistäminen parantaa tarkuutta merkittävästi on varmistettu, että seuraava luokka ehdot
täyttäessäänkään ei voi liittyä jo yhdistettyyn luokkaan vaan sen kohdalla tehdään oma laskelma sitä
seuraavaa luokkaa varten. Tämän vuoksi yhdistysmerkintä tehdään tarvittaessa loopin kohdalla olevaan
ja sitä seuraavaan luokkaan merkitsemällä kummatkin yhdistysjärjestyksen mukaisella luvulla, joka
kasvaa jokaisen yhdistyksen yhteydessä ja jonka avulla loopin tullessa jo yhdistetyn luokan kohdalle
voidaan estää sitä yhdistämästä sitä seuraavaa luokkaa. Lopulta ulos tulee alkuperäisten luokkien
määrän kokoinen vektori, jossa yhdistämättömät luokat on merkitty 0:lla ja yhdistettävät ovat
vierekkäiset samalla luvulla merkityt.

Mikäli kaikki luvut yhdistysvektorissa ovat nollia, ohitetaan seuraava vaihe ja kirjoitetaan
luokkien alueet suoraan exceliin. Muussa tapauksessa siirrytään tekemään keskiarvon- ja
SD:nlaskennat uusille luokille. Yhdistämättömien kohdalla tämä ei poikkea juurikaan alunperin
tehdystä, mutta yhdistettävän luokan osuessa kohdalle täytyy ottaa suurempia alue ratioista ja
käyttää appender muuttujaa varmistamaan, että uudet luvut kirjoitetaan uuden luokan kohdalle, mutta
siten, ettei toisen yhdistettävän luokan tilalle jää tyhjää. Niinpä appender muuttuja kasvaa
jokaisen yhdistettävän luokan kohdalla yhdellä ja siirtää sen jälkeen tulevien kirjoituskohtaa
vastaavasti taaksepäin. Näin lopputuloksena on yhdistettyjen luokkien mittainen keskiarvovektori.

Lopulta keskiarvot puolittamalla saadaan raja-arvot, joissa kunkin luokan ala- ja ylärajat menevät
ja ne kirjoitetaan exceliin luokittelijaa varten.

Classifier.py:

Luokittelija on hyvin yksinkertainen, se lukee opetusalgoritmin tulokset luokista ja kutsuu
multi_img.py:tä analysoimaan testikuvat niiden luokittelua varten. Lukemisen ja kirjoituksen ohella
algoritmissä ei tapahdu juuri muuta kuin kaikkien kuvien ration vertaus luokkien raja-arvoihin
siten, että jos tulos on suurempi tai yhtä suuri kuin loopin kohdalla olevan luokan raja-arvo ja
pienempi kuin sitä seuraavan luokan, kuuluu kyseinen kuva kyseiseen luokkaan.

Lopuksi kirjoituksen jälkeen luokittelija kutsuu tarkkuuden laskentaa (accuracy.py). Huomioitavaa
on, että koska testikuville ei ole vielä omaa luokitustaan tarkkuuden laskenta hakee referenssit
alkuperäisten opetuskuvien luokista. Joten kunnes se on implementoitu täytyy opetuskuvia ja
testikuvia olla yhtä paljon kussakin alkuperäisessä luokassa.

Multi_img.py:

Algoritmi käy läpi argumenttina annetun kansion kaikki kuvat jättäen huomiotta kaikki siellä olevat
ei-kuvatiedostot. Multia voi kutsua joko opetusalgoritmi tai luokittelija. Multi erottaa ne
toisistaan niiden lähettämän caller muuttujan arvon avulla ja päättää sen perusteella minkä niminen
excel kirjoitetaan.

Itse algoritmi lukee kuvan värillisen ja tekee siitä harmaasävyversion. Kumpaakin kuitenkin
tarvitaan, sillä kummastakin otetaan cropilla keskikohdat eri tarkoituksiin. Algoritmi myös lukee
viivan hakuun käytetyn templaten, jonka korkeutta ja leveyttä kuvaavat muuttujat skaalataan kuvan
koon mukaan, sillä niitä käytetään myöhemmin eri laskennoissa.

Template matchingia käyttäen kuvasta etsitään argumenttina annetun tyyppistä testialuetta ensin
keskeltä cropatusta harmaasävykuvasta ja jos se ei löydy sieltä edes C-viivan etsintäaluetta
laajentamalla (35-45% vasemmalta), niin sitä etsitään koko kuvasta. C-viivan täytyy vastata
vähintään 70%:sti templatea, jotta se hyväksytään. C-viivaa etsitään jakamalla keskialue kahtia,
sillä se estää templatea löytämästä T-viivaa mikäli se on tummempi kuin C-viiva.

Kun C-viiva on löydetty tehdään keskialueen kuville bilateral suodatus. Se on suhteellisen raskas,
joten sitä kannattaa käyttää vain pieneen osaan kuvasta. Raskauden vastineeksi se osaa suodattaa
kuvaa hävittämättä kuvassa olevia reunoja näin säästäen viivat ehjinä.

C-viivan sijainnin perusteella haetaan identtisestä värikuvan cropista C-viivan keskikohta ja
lasketaan sen rgb-arvot. Vertaamalla kutakin rgb-arvoa ympärillä olevaan alueeseen päätetään millä
värikanavalla on suurin kontrasti testialueen taustan kanssa ja se eristetään uudeksi
harmaasävykuvaksi, josta ratiot lopulta lasketaan. Tämän vuoksi C-viivan keskikohta haetaan siitä
uudestaan, jotta sen intensiteetin keskiatvo voidaan laskea siitä.

C-viivan sijainnin ja templaten leveyden perusteella voidaan cropata alue C-viivasta oikealle ilman
että itse C-viiva jää kuvaan. Mahdollisimman suuren kontrastin värikanavan haun lisäksi tälle
kuvalle tehdään sekä manuaalinen kontrastin nosto, että clahen kontrasti. Clahe on normaalia
automatisoitua kontrastin vahvistusta älykkäämpi, sillä se huomioi ympäröivät alueet ja lisäksi sen
voimakkuudet ovat säädettävissä.

Kun T-viivasta on vahvistusten jälkeen laskettu sen X-akselin arvot yhteen haetaan sen kohtaa raja
-arvon avulla, joka lasketaan ottammalla pienempi alue T-viivan cropatun kuvan keskeltä ja
laskemalla sen intensiteetin keskiarvo, jota pudotetaan hieman. Tästä muodostunut vektori käydään
läpi for-loopilla, joka laskee mistä raja-arvon alittavat arvot alkavat ja myös kuin pitkään ne
jatkuvat. Jos kyseinen pätkä on tarpeeksi pitkä ja ehjä sen päätellään olevan T-viiva. Loopissa on
myös tolerance muuttuja, joka oli tarkoitettu pienten häiriöiden sietämiseen, mutta on sittemmin
käynyt turhaksi ja sen arvo on siten 0. Sen voisi poistaa, mikä yksinkertaistaisi looppia
merkittävästi.

Koska clahe leventää viivaa korostamassaan kuvassa, sitä varten tehdään templaten koon avulla
skaalaus, jotta viiva ei ole leveämpi kuin template eli käytännössä C-viiva. Oletus on, että
leventyneessäkin viivassa oikea viiva on sen keskellä ja testauksen perusteella näin on aina.
Skaalausarvojen, loopin tulosten ja C-viivan paikan avulla voidaan laskea T-viivan paikka.

T-viiva ja sen lähialue croptaan myös aiemmin valitulta rgb-kanavalta. Lähialueelta saadaan
laskettua testialueen taustan intensiteetti, , kun taas T-viivalle tehdään samanlainen intensiteetin
arvon laskenta keskeltä kuin C-viivallekkin. Kummankin viivan intensiiteetti lasketaan viivan
keskellä olevalta alueelta, jotta mahdolliset testiin alueen vinossa olot eivät haittaa ration
laskentaa vaikka viivan oletetun alueen ala- tai yläosaan tulisikin jotain muuta.

Kun intensiteettit on laskettu tarkastellaan kuinka voimakassävyinen T-viiva on. Jos se on skaalalla
0-100 heikompi kuin 0.1 sen oletetaan olevan kohinaaa ja ohitetaan suoraan liian heikkona. Jos se on
matalampi kuin 1,0 tarkastetaan template matchingillä, että kyseessä todella on viiva. T-viivan
alueelle tehdään kontrastin muutos ja clahe uudestaan sekä template skaalataan cropatun alueen
kokoiseksi, koska jos se on isompi jossain suunnassa siitä aiheutuu virhe. Mikäli T-viivan todella
vahvistettu versio on alle 50% match se hylätään roskana/kohinana. Suuren intensiiteetin T-viivoille
tätä tarkistusta ei tehdä, koska ne erottuvat helpommin ja kontrastin vahvistukset vahvistavat niitä
niin paljon, että ne eivät mene template matchingista läpi.

Lyhyesti algoritmissä tehdään T-viivan alueelle suodatuksia ja vahvistuksia kuitenkaan muuttamatta
alkuperäistä kuvaa merkittävästi. Sijaintien ja kokojen muistiin tallentamisten avulla T-viiva
voidaan hakea muokkaamattomasta kuvasta, kun se on ensin löydetty vahvasti muokatuista.

Line_detection.py ja single_img.py:

Line_detection on jäänne, mutta sen avulla kutsutaan single_img.py:tä. Single on samanlainen kuin
multi_img.py, mutta se ottaa vain yhden kuvan. Se on hyvä testaamiseen koska se on nopeampi ja
helpompi havainnoimaan kuvankäsittelyn eri vaiheita. Multi_img ei edes tulosta virheilmituksia,
mikäli jokin on ongelmana. Se vain pyörii läpi eikä anna tuloksia.

Konsolikomennot:
python classifier_teach.py --tl 50 --template Test_Template.png --dir tests/
python classifier.py --tl 50 --template Test_Template.png --dir tests/
python line_detection.py --tl 50 --template Test_Template.png --image tests/04_06.png

