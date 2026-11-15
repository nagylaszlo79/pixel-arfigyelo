# Pixel 10 Pro árfigyelő

Statikus weboldal, helyi kézi ajánlatrögzítéssel és GitHub Actions segítségével 6 óránként frissülő, **korlátozott** automatikus adatkinyeréssel.

## Közzététel

1. Hozz létre egy új **nyilvános** GitHub repositoryt.
2. Töltsd fel a csomag **teljes tartalmát** a repository gyökerébe, a rejtett `.github` mappát is.
3. A GitHub repository **Settings → Pages → Build and deployment → Source** menüjében válaszd a **GitHub Actions** lehetőséget.
4. Az **Actions → Frissítés és közzététel → Run workflow** gombbal indítsd el a futást. A Pages címet a telepítés után a GitHub megmutatja.
5. Az automatikus forrásellenőrzés kb. 6 óránként indul (a GitHub ütemezése késhet).

## Korlátok

- A kezdeti két forrás kategória-/hirdetéslista, amelyből **nem garantált**, hogy termékadatot lehet kinyerni. Az ellenőrzés JSON-LD Product adatokat keres, és csak a pontos Pixel 10 Pro, 256 GB vagy nagyobb változatokat kezeli; a 10a/XL/Fold kizárt.
- A `sources.json` fájlba célszerű konkrét, megfelelő termékoldalakat felvenni (név, ország, URL). Csak nyilvánosan elérhető oldalakkal működik; botvédelem vagy eltérő HTML esetén nem.
- A szállítási költség, garancia, készlet, új/bontatlan állapot nem ellenőrizhető megbízhatóan automatikusan. A kinyert adatok külön blokkban szerepelnek, nem számítanak igazolt, 350 000 Ft alatti ajánlatnak.
- Az EUR/PLN árfolyam **kézzel beállítható**, nem élő.
- A kézi ajánlatok a böngésző helyi tárhelyén maradnak; a GitHubra nem kerülnek fel és másik eszközre nem szinkronizálódnak.
- A weboldal nem küld önmagában értesítéseket. A korábban beállított külön ChatGPT árfigyelési feladat ettől független.
- A nyilvános repositoryba ne tegyél személyes adatot vagy titkos kulcsot.
