#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
class Bunch:
    """
    Useful for mocking class instances.

    In python, you cannot access dictionary keys with .[prop] notation,
    e.g. you can access a property like this `mydict['myprop']`
    but not like this `mydict.prop`

    So when you want to mock an object that has properties,
    you can't just use a dictionary. You *can* instead
    just use Bunches like this:

    ```
    myObj = Bunch(
        myProp = Bunch(myNestedProp = 'a')
    )

    print(myObj.myProp.myNestedProp) # prints 'a'
    ```
    """

    def __init__(self, **kwds):
        self.__dict__.update(kwds)
