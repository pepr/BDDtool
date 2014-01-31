Požadavek: vytvoření plánu z výsledku analýzy

Jako běžný uživatel
chci vytvořit plán z výsledku analýzy,
protože ruční vytváření plánu je pracné.

Rozbor: Plán má podobu datové kostky. V APSm3 jej může vytvářet jen uživatel,
který má oprávnění pracovat se Správcem číselníků a plánů. Dokud nebude možné
vytvářet lokální plány, nemůže být daný požadavek splněn pro "běžného uživatele".
V dalších verzích by to mohlo jít i pro běžného uživatele, který by si mohl
vytvářet některé lokální datové kostky.


Scénář: schopnost zjistit existující kostku plánu pro danou analýzu
  Dáno: vlastnosti (typ, atributy) analýzy
  Když: vyhodnotíme atributy analýzy
     a: kostka plánu existuje
   Pak: jsme schopni vrátit atributy existující kostky plánu


Scénář: schopnost zjistit neexistenci kostky plánu pro danou analýzu
  Dáno: vlastnosti (typ, atributy) analýzy
  Když: vyhodnotíme atributy analýzy
     a: kostka plánu neexistuje
   Pak: jsme schopni vrátit atributy budoucí kostky plánu


Scénář: schopnost vytvořit prázdnou kostku plánu
  Dáno: analýza s prázdným výsledkem
  Když: neexistuje kostka odpovídající příslušným atributům
     a: necháme uložit výsledek jako nový plán
   Pak: přidělí se atributy vznikajících struktur
     a: vznikne prázdná kostka s dimenzemi odpovídajícími typu analýzy


Scénář: schopnost vytvořit novou naplněnou kostku plánu
  Dáno: jednoduchá analýza podél jedné dimenze s konkrétními výsledky
  Když: neexistuje kostka odpovídající příslušným atributům
     a: necháme uložit výsledek jako nový plán
   Pak: vznikne nový plán
