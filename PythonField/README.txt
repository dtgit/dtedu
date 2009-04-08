PythonField Readme

  An Archetype field that stores Python scripts.

  Usage
  
    1. Install as usual in your Products directory.

    2. Add this line to your custom Archetype to import the field::
    
        from Products.PythonField import PythonField

    3. In your schema, add PythonField like this::
    
        BaseSchema + Schema(( ...
            PythonField('myField'),
            ...
        ))

  Further Information

   Visit http://plone.org/products/scriptablefields for documenttion, 
   bug-reports, etc.

  Credits

    Thanks to Sidnei da Silva for the TALESField product, which served
    as the base for this.

  Copyright
  
    Copyright (C) 2005-2007 BlueDynamics Alliance, Klein & Partner KEG, Innsbruck, Austria
