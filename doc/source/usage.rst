=====
Usage
=====

To use python-brick-cinderclient-ext in a project::

    import brick_cinderclient_ext
    from cinderclient import client

    c = client.Client(2, extensions=[brick_cinderclient_ext])
    print(c.brick_client_ext.get_connector())
