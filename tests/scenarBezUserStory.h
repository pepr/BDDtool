// Požadavek: vytvoření generátoru testů pro C++ kód

// Scénář: 
SCENARIO("scénářbez začítá slovem \"Scénář\" nebo \"Scenario\"") {
    GIVEN("soubor se scénáři") {
        WHEN("slovo \"scénář\" nebo \"scenario\" je nalezeno na začátku řádku") {
            THEN("následuje definice scénáře") {
            }
        }
    }
}
// scenario: 
SCENARIO("X velikost písmen u klíčových slov nehraje roli") {
    GIVEN("soubor se scénáři") {
        WHEN("slovo \"scénář\" nebo \"scenario\" obsahuje velká písmena") {
            THEN("klíčové slovo je detekováno bez ohledu na velikost písmen") {
            }
        }
    }
}
// Příklad: 
SCENARIO("X alternativní začátek definice scénáře v češtině") {
    GIVEN("toto je zápis scénáře") {
    }
}
// Example: 
SCENARIO("X alternativní začátek definice scénáře s anglickým klíčovým slovem") {
    GIVEN("toto je zápis scénáře") {
    }
}
