=============
Specification
=============

This chapter contains the specification for WAStD.


High level business requirements
================================
Framework maturity
------------------
R: The application must be written in an industrial-strength, mature framework.
The chosen framework and solution architecture should not require significant
rewrites in the forseeable future.

A: Django and PostgreSQL / PostGIS are part of the Parks & Wildlife
Standard Operating Environment (SOE) and are preferred technologies. BioSys and
SDIS are written in the same framework.
To keep the application secure and up to date, roughly once per year it should
be updated to the latest Django version, and update utilised third-party libraries
as well. The "requirements" flag on the top of this documentation indicates whether
the underlying frameworks and libraries are up to date, outdated, or insecure.

Capacity
--------
R: The application must be able to handle all turtle stranding and tagging data.

A: The database and application framework support millions of records easily.
Performance enhancements will be implemented as data grows. E.g., the map on the
home page will not show all data by default, but will be restricted (and filterable)
to a smaller, relevant subset. Long running operations, such as reconstructing
animal names, can be run asynchronously in the background.

Accessibility and security
--------------------------
R: The application must be accessible from the web to Parks & Wildlife staff now,
and possibly be public facing with the addition of registered, non-departmental users.
The users' connections must be secure.

A: The application is hosted as web application with encrypted data transmission
(HTTPS). Users are authenticated with Parks & Wildlife's Single Sign On (SSO)
authentication, provided by Microsoft Online. The application also supports
self-registration for non-departmental users, which currently is hidden behind
the SSO mechanism. The application is as of now accessible to regional staff.

User management
---------------
R: The application needs to support different user groups with different permissions,
such as data custodians (full access), data entry operators (restricted access to
data entry forms, review own work, but not others'), general view (read-only access
to all or only data marked as fit for analysis).

A: Currently, every Parks & Wildlife staff member has public access. Selected,
trained operators (some Marine Science staff) have data custodian-level access to
enter, update and review all data. If required, the system can be extended so that
access to any part of the system is restricted to arbitrary groups, to which users
can be allocated by higher privileged users.

The current permission system works for legacy data entry by Marine Science staff
and analysis by other selected staff.
If regional users join the data entry effort, additional functionality can easily
be added to support their workflows.

Compatibility with other systems
--------------------------------
R: The application has to be compatible with Queensland's StrandNet, Parks &
Wildlife's Turtle Tagging database WAMTRAM 2, and the Ningaloo Turtle Program's
track count database.

A: Pending review and possible addition of dropdown options, WAStD is compatible
to these systems in that data can be exchanged between these systems with a simple
mapping of lookup values.

Data entry
----------
R: The application needs to support the entry and curation of existing legacy stranding
records, which exist as paper records, digital files, and database entries in WAMTRAM 2.
The data model needs to support all data that is contained within legacy records
and database systems.

A: The application supports data entry from paper and digital files as described
in chapter Data Curators > Turtle Stranding. Database records from the NTP
database and WAMTRAM 2 can be imported through scripts (RMarkdown workbooks),
which are currently in development (ETA late 2016).

Data analysis
-------------
R: The application must provide means to filter and export data into standard
formats.

A: The application supports that, as documented in chapter Data Consumers.

Scope
-----
R: The application must support Turtle Strandings now, but be extensible to
handle strandings of other species (sea snakes, dolphins, whales, seals), and
to turtle data other than strandings (tagging, nesting, tracks).

A: The application currently supports turtle stranding and tagging, as well as
turtle track counts and individual nest encounters. The application can be extended
easily to accommodate observations specific to other species (e.g. measurements
taken after cetacean strandings).
