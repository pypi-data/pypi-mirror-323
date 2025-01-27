Landowner
=========

Overview
--------

Landowner is a Python package designed to work with the JSON files that social media platforms provide when you request a copy of your personal data. This project aims to provide tools to parse, analyze, and manage your personal data efficiently.

Features
--------
- Parse complex JSON files from social media platforms into a structured format using straightforward classes with attributes.
- Deserializers for exports from Meta social media platforms are supported, including Facebook and Instagram.
- Support for handling mojibaking and other encoding issues with post content.


Future Features
---------------
- Deserializers for other social media platforms, such as X (formerly Twitter).

Installation
------------

To install the project, use pip:

.. code-block:: bash

    pip install landowner


You can also clone the repository and install the required dependencies:

.. code-block:: bash

    git clone https://github.com/loranallensmith/landowner.git
    cd landowner
    pip install -r requirements.txt


Usage
-----

To start using the project, run the following command:

.. code-block:: bash
    
    import json
    from landowner.deserializers import FacebookExportPostDeserializer

    ds = FacebookPostExportDeserializer()
    
    with open('path/to/facebook.json') as f:
        data = json.load(f)

    posts = ds.deserialize(data)

Contributing
------------

Contributions are welcome! Please fork the repository and submit a pull request.

License
-------

This project is licensed under the GNU General Public Licence v3.0. See the LICENSE file for more details.

Contact
-------

For any questions or inquiries, please contact Drop Table Records at info@droptablerecords.com.