.. _customtype:

Custom types
============

You can add support for serializing and deserializing custom types like this::

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

    # Deserizalize
    # will return MyMessageType('Hello')
    user.settings.get('myproperty', as_type=MyMessageType)
