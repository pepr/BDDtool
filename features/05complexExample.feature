Story: BDD oriented complex example

    As a normal user
    I want to capture this case that shows the way of prescribing my acceptance
    so that I am able to express my requirements without programming.

Scenario: vectors can be sized and resized
     Given: A vector with some items
      When: more capacity is reserved
      Then: the capacity changes but not the size

Scenario: given when and then -- more free form
    Given the description in the free form,
    when the identifiers contain punctuation,
    then the punctuation is stripped.

Test: this is actually related to the coders who use Catch (i.e. for programmers)
    Sec: section 1
    Sec: section 2
    Sec: section 3
  