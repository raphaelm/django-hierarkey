.. _customtype:

Custom types
============

You can easily add support for serializing and unserializing custom types, for example like this::

    class MyMessageType:
        def __init__(self, msg):
            self.msg = msg

    hierarkey.add_type(
        MyMessageType,
        lambda v: v.foo,
        lambda v: MyMessageType(v)
    )

    ...

    # Serialize
    user.settings.set('myproperty', MyMessageType('Hello'))

    # Unserizalize
    # will return MyMessageType('Hello')
    user.settings.get('myproperty', as_type=MyMessageType)
