Požadavek: vytvoření generátoru testů pro C++ kód

User story:
    Jako běžný uživatel
    chci vytvořit generátor testů pro C++ kód ze srozumitelného textového popisu,
    protože ruční vytváření testů je příliš "daleko" od myšlení při analýze.


Scénář: scénář začítá slovem "Scénář" nebo "Scenario"
  Dáno: soubor se scénáři
  Když: slovo "scénář" nebo "scenario" je nalezeno na začátku řádku
   Pak: následuje definice scénáře


   scénář:  bílé znaky na začátku definičního řádku nehrají roli
   Dáno: soubor se scénáři
   Když: slovo "scénář" je uvozeno jednou nebo více mezerami či tabulátory
    Pak: úvodní bílé znaky se ignorují

scenario: velikost písmen u klíčových slov nehraje roli
  Dáno: soubor se scénáři
  Když: slovo "scénář" nebo "scenario" obsahuje velká písmena
   Pak: klíčové slovo je detekováno bez ohledu na velikost písmen

Scénář: klasický začátek scénáře v češtině
  Dáno: toto je zápis scénáře

scenario: klasický začátek definice scénáře s anglickým klíčovým slovem
  Dáno: toto je zápis scénáře

Příklad: alternativní začátek definice scénáře v češtině
  Dáno: toto je zápis scénáře

Example: alternativní začátek definice scénáře s anglickým klíčovým slovem
  Dáno: toto je zápis scénáře

Scenario: definice scénáře bez detailu za klíčovým slovem
  Dáno: soubor s definicemi scénářů
  Když: za slovem "scénář"

Scenario: titulek scénáře začíná za dvojtečkou
  Dáno: soubor s definicemi scénářů
  Když: za slovem "scénář"

Scénář : analytické popisy se oddělují do samostatných souborů
  Dáno: adresář se soubory s příponou jmeno.feature
  Když: nalezneme jmeno.feature
   Pak: bude po zpracování existovat jmenoTest.h
     a: vygenerovaný výsledek bude zařazen mezi testované

Scénář : požadavek bez scénářů nevygeneruje žádné testy
  Dáno : existující soubor.feature
  Když : obsah souboru nedefinuje žádný scénář
   Pak : nebude vygenerován žádný spustitelný test
