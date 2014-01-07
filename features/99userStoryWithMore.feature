Story: vytvoření generátoru testů pro C++ kód

    Jako běžný uživatel
    chci vytvořit generátor testů pro C++ kód ze srozumitelného textového popisu,
    protože ruční vytváření testů je příliš "daleko" od myšlení při analýze.


Scénář: scénář začítá slovem "Scénář"
  Dáno: soubor se scénáři
  Když: výše uvedené slovo je nalezeno na začátku řádku
   Pak: následující definice je rozpoznána jako definice scénáře

Scenario: scénář začítá slovem "Scenario"
   Given: soubor se scénáři
    When: výše uvedené slovo je nalezeno na začátku řádku
    Then: následující definice je rozpoznána jako definice scénáře

Příklad: scénář začítá slovem "Příklad"
   Dáno: soubor se scénáři
   Když: výše uvedené slovo je nalezeno na začátku řádku
    Pak: následující definice je rozpoznána jako definice scénáře

Example: scénář začítá slovem "Example"
  Given: soubor se scénáři
   When: výše uvedené slovo je nalezeno na začátku řádku
   Then: následující definice je rozpoznána jako definice scénáře

   scénář  :  bílé znaky a velikost písmen při rozpoznávání nehrají roli
   dáno    : soubor se scénáři
   když    : klíčové slovo je uvozeno mezerami a mezery jsou kolem dvojtečky
    pak    : nadbytečné bílé znaky se ignorují

Scénář : požadavek bez scénářů nevygeneruje žádné testy
  Dáno : existující soubor.feature
  Když : obsah souboru nedefinuje žádný scénář
   Pak : nebude vygenerován žádný spustitelný test, ale soubor .h ano
