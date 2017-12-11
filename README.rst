Acapela Group
=============

.. image:: https://travis-ci.org/Ge0/acapela-group.svg?branch=master
    :target: https://travis-ci.org/Ge0/acapela-group

.. image:: https://coveralls.io/repos/github/Ge0/acapela-group/badge.svg?branch=master
    :target: https://coveralls.io/github/Ge0/acapela-group?branch=master

Acapela Group is a python module that lets you extract text-to-speech
generated mp3 urls from http://www.acapela-group.com with the provided
parameters such as language, selected voice and text.

At the moment, this package is only supported for python >= 3.6. Feel free
to open a pull request to ask for previous version support if you are
interested in the project!


Installation
------------

Setup with:

.. code-block:: bash

    python setup.py install


Usage
-----

You can use acapela-group either through the command line:

.. code-block:: bash

    $ acapela-group "French (France)" "AntoineFromAfar (emotive voice)" \
        "Ce module est développé par un français."
    http://H-IR-SSD-1.acapela-group.com/MESSAGES/012099097112101108097071114111117112/AcapelaGroup_WebDemo_HTML/sounds/61006110_e6d5342c9a6b5.mp3

Or as a library:

.. code-block:: python

    from acapela_group.base import AcapelaGroup

    acapela_group = AcapelaGroup()
    # Optional: you can authenticate against the website, so the generated
    # sounds won't have that stupid background music spoiling everything.
    acapela_group.authenticate('username', 'password')

    print(acapela_group.get_mp3_url('French (France)',
                                    'AntoineFromAfar (emotive voice)',
                                    'Tout ça à cause de Sloman'))
