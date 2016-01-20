Story: Elaborate description can be placed in comment blocks

    As a normal user
    I want some descriptions can be marked as comment blocks
    so that the text is completely ignored.

/*
Details: The comment blocks uses C syntax. All lines inside are not interpreted.
The lines are only passed as a comment to the generated skeleton -- that means
as is, including the comment parentheses.

The consequence is that the lines can contain also free-form keywords inside.

Another consequence is that the comment block can be used to comment-out
some existing scenario like this...

Scenario: vectors can be sized and resized
     Given: A vector with some items
      When: more capacity is reserved
      Then: the capacity changes but not the size

In other words, this feature file will not generate any scenario construct.
*/

    /* This is one-liner C-comment block */

/* This is C-comment line on the same line where the opening starts
and this is the line when the close sequence appear. */

// This
// block
// of lines
// is commented
// by C++ comments.
