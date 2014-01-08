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
    Sec: sections act as Given, When, Then, but they are not problem related
    + Sec: one level nesting
    + Sec: also one level nesting, i.e. processed after the previous one
    + + Sec: two level nesting
    | Sec: possible alternative of maring the nesting (nicely allign)
    | | Sec: alternative two level nesting
    & Sec: another alternative character, nested one level
    & & Sec: another alternative -- nested two levels
          Sec: this is probably too fragile for normal users
          Sec: this and previous should not be considered nested
    Sec: the previous two should be at the same logical level as this one
Sec: even this should be at the same level as the first one

Sec: empty line should be skipped, but...
     continuation lines are questionable this should be just a line.
     The way could be to convert the continuation lines to comments.
     This would help programmer to plan
  