This product provides two Archetype fields that store and render
templates.  There's the DTMLField for DTML templates and the
ZPTField for ZPT templates.

Usage
=====
  
1. Install as usual in your Products directory or as an egg.

2. Add this line to your custom Archetype to import the fields::

    from Products.TemplateFields import DTMLField, ZPTField

3. In your schema, add DTMLFields and ZPTFields like this::

        BaseSchema + Schema(( ...
            DTMLField('oneField'),
            ZPTField('anotherField'),
            ...
        ))

Credits
=======

Thanks to Sidnei da Silva for the TALESField product, which served
as the base for this.

Further Information
===================

Visit http://plone.org/products/scriptablefields for documentation,
bug-reports, etc.

Copyright
=========

(C) 2005-2007, BlueDynamics Alliance, Klein & Partner KEG, Austria

