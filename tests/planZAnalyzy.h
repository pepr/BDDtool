// Požadavek: vytvoření generátoru testů pro C++ kód

// User story:
//     Jako běžný uživatel
//     chci vytvořit generátor testů pro C++ kód ze srozumitelného textového popisu,
//     protože ruční vytváření testů je příliš "daleko" od myšlení při analýze.

// Scénář: 
SCENARIO("scénář začítá slovem \"Scénář\" nebo \"Scenario\"") {
GIVEN("soubor se scénáři") {
WHEN("slovo \"scénář\" nebo \"scenario\" je nalezeno na začátku řádku") {
THEN("následuje definice scénáře") {

// scénář:  
SCENARIO("bílé znaky na začátku definičního řádku nehrají roli") {
GIVEN("soubor se scénáři") {
WHEN("slovo \"scénář\" je uvozeno jednou nebo více mezerami či tabulátory") {
THEN("úvodní bílé znaky se ignorují") {

// scenario: 
SCENARIO("velikost písmen u klíčových slov nehraje roli") {
GIVEN("soubor se scénáři") {
WHEN("slovo \"scénář\" nebo \"scenario\" obsahuje velká písmena") {
THEN("klíčové slovo je detekováno bez ohledu na velikost písmen") {

// Scénář: 
SCENARIO("klasický začátek scénáře v češtině") {
GIVEN("toto je zápis scénáře") {

// scenario: 
SCENARIO("klasický začátek definice scénáře s anglickým klíčovým slovem") {
GIVEN("toto je zápis scénáře") {

// Příklad: 
SCENARIO("alternativní začátek definice scénáře v češtině") {
GIVEN("toto je zápis scénáře") {

// Example: 
SCENARIO("alternativní začátek definice scénáře s anglickým klíčovým slovem") {
GIVEN("toto je zápis scénáře") {

// Scenario: 
SCENARIO("definice scénáře bez detailu za klíčovým slovem") {
GIVEN("soubor s definicemi scénářů") {
WHEN("za slovem \"scénář\"") {

// Scenario xyz: 
SCENARIO("titulek scénáře začíná za dvojtečkou") {
GIVEN("soubor s definicemi scénářů") {
WHEN("za slovem \"scénář\"") {

// Scénář 1: 
SCENARIO("analytické popisy se oddělují do samostatných souborů") {
GIVEN("adresář se soubory s příponou jmeno.feature") {
WHEN("nalezneme jmeno.feature") {
THEN("bude po zpracování existovat jmenoTest.h") {

// Scénář 2: 
SCENARIO("požadavek bez scénářů nevygeneruje žádné testy") {
GIVEN("existující soubor.feature") {
WHEN("obsah souboru nedefinuje žádný scénář") {
THEN("nebude vygenerován žádný spustitelný test") {

