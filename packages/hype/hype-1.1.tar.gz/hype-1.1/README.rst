====
hype
====

A Python library for flexible resource mapping and API development. Hype provides a powerful way to define, traverse, and transform resources with support for multiple output formats including JSON, WAC-JSON, and URL-encoded forms.

Features
--------

* Resource mapping and traversal with cycle detection
* Multiple output format support (JSON, WAC-JSON, API-JSON, URL-encoded)
* Field-based resource definition with type validation
* Automatic URL generation and linking between resources
* Pagination support with cursor-based navigation
* Flexible resource transformation pipeline
* Thread-safe global context management

Installation
------------

.. code-block:: bash

    pip install hype

Requirements
------------

* Python 2.7

Usage
-----

Here's a quick example of defining and transforming a resource:

.. code-block:: python

    from hype import Resource, fields
    
    class User(Resource):
        name = fields.String()
        email = fields.String()
        profile = fields.Link(endpoint='profile.show')
    
    # Transform to JSON
    from hype.mime import application_json
    
    def url_for(ref):
        return f'/api/{ref.name}/{ref.params["id"]}'
    
    user = User(name='John Doe', email='john@example.com')
    json_output = application_json.serialize(user, url_for=url_for)

Documentation
-------------

Full documentation is available at https://github.com/balanced/hype/

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request.

License
-------

This project is licensed under the ISC License - see the LICENSE file for details.

Author
------

Balanced Developers (dev@balancedpayments.com)
@bninja
@mahmoudimus
@mjallday
