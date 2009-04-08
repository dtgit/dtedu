SQLPASPlugin

  A set of sql-based plugins for PAS.

Requirements

  See DEPENDENCIES.txt

Information

  SQLPASPlugin currently provides three primary pieces. One for
  providing authentication against a SQL-based data source, one for
  the reading and writing of user property sheets from a SQL-based
  data source and another for dealing with roles.

  The unit tests are configured to run against SQLite by default. But
  these tests can be configured to run against any other SQL data
  source. There is currently setup information commented out for
  running the tests against PostgreSQL and MySQL as well.

  Note: Currently SQLPASPlugin is dependent upon PlonePAS for writing
  properties back to the SQL datasource. The plan in the future would
  be to remove the requirement on PlonePAS.

Authors

  - Rocky Burt <rocky@serverzen.com> of ServerZen Software

  - Nate Aune <natea@jazkarta.com> of Jazkarta

Contributors

  - Ruda Porto Filgueiras <rudazz@gmail.com>

  - Daniel Nouri <daniel.nouri@gmail.com>

  - Dorneles Treméa <deo@jarn.com> of Jarn
  
  - Wichert Akkerman <wichert@jarn.com> of Jarn

Credits

  - Thanks to ChemIndustry.com Inc. for financing the development of
    SQLPASPlugin

  - Thanks to Statens Byggeforskninginstitut (http://www.sbi.dk) for sponsoring
    the caching support.

License

  GNU GPL v2 (see LICENCE.txt for details)
