#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the Catch test sources.'''

import lexan
import textwrap



def start()


#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = textwrap.dedent('''\
        // Story: story identifier
        //
        //  As a user
        //  I want the feature
        //  so that my life is to be easier.

        SCENARIO( "name for scenario", "[optional tags]" ) {
            GIVEN( "some initial state" ) {
                // set up initial state

                WHEN( "an operation is performed" ) {
                    // perform operation

                    THEN( "we arrive at some expected state" ) {
                        // assert expected state
                    }
                }
            }
        }
        ''')

    for lexitem in lexan.Container(source):
        print(lexitem)