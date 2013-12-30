Požadavek: vytvoření generátoru testů pro C++ kód

Scénář: scénářbez začítá slovem "Scénář" nebo "Scenario"
  Dáno: soubor se scénáři
  Když: slovo "scénář" nebo "scenario" je nalezeno na začátku řádku
   Pak: následuje definice scénáře
   
   
scenario: X velikost písmen u klíčových slov nehraje roli
  Dáno: soubor se scénáři
  Když: slovo "scénář" nebo "scenario" obsahuje velká písmena
   Pak: klíčové slovo je detekováno bez ohledu na velikost písmen
   
Příklad: X alternativní začátek definice scénáře v češtině
  Dáno: toto je zápis scénáře
   
Example: X alternativní začátek definice scénáře s anglickým klíčovým slovem
  Dáno: toto je zápis scénáře
