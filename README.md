# Keskustelusovellus

Sovellus on kehitetty harjoitustyönä Helsingin Ylipoiston Tietokantasovellus-kurssilla.

## Kuvaus

* Käyttäjät voivat kirjautua sisään ja ulos, sekä luoda uuden tunnuksen
* Käyttäjä voi luoda uuden ketjun olemassaolevalle keskustelualueelle syöttämällä otsikon ja avausviestin sisällön, sekä valinnaisesti linkin
* Käyttäjä voi muokata tai poistaa oman viestinsä tai ketjunsa
* Käyttäjä voi vastata olemassaolevaan ketjuun, tai ketjun viesteihin
* Käyttäjät voivat antaa viesteille "tykkäyksiä". Ketjun vastaukset järjestetään ensisijaisesti tykkäysten mukaan
* Sovelluksen etusivu näyttää käänteisen kronologisen listan uusimmista ketjuista
* Keskustelualueiden sivu näyttää käänteisen kronologisen listan uusimmista ketjuista
* Käyttäjä voi luoda uuden keskustelualueen syöttämällä nimen joka ei ole vielä käytössä. Käyttäjä saa hallinnointioikeudet luomaansa keskustelualeeseen
* Keskustelualueille voi hallinnoitsijan toimesta asettaa käyttäjäluokka- että käyttäjäkohtaisia oikeuksia, esimerkiksi: ketjujen näkyvyys, oikeus aloittaa ketju, oikeus vastata ketjuun
* Keskustelualueen hallinnoitsijat voivat piilottaa (jolloin ketjusta näkyy vain tynkä) tai poistaa ketjuja ja viestejä hallinnoimillaan alueilla, sekä antaa muille käyttäjille vastaavanlaiset oikeudet
* Sivuston ylläpitäjät voivat hallinnoida keskustelualueita ja niiden oikeuksia, sekä poistaa käyttäjiä tai keskustelualueita.
* Sivuston vierailijat voivat hakea avainsanoilla keskustelualueita, ketjuja, ja ketjujen sisältöä

## Tietokantakaavio

![Database Schema](https://github.com/chzesa/uni-tsoha/blob/master/docs/schema.png)