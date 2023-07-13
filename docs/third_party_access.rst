.. _3pa:

******************
Third party access
******************

If you are DBCA staff and not yet signed in, or if you are an external user, 
visiting WAStD will redirect you to the DBCA Auth2 page to authenticate through DBCA Microsoft 365
or sign in/up using a Microsoft account, Google, or an arbitrary email.

The allowed domains of arbitrary email accounts are restricted to the set of known external users.

On first login, you will land on the "Welcome! Permission denied" page. 
Your access attempt will be logged and we will be in touch once your permissions have been assigned. 
Once permissions have been assigned, you can login again and will get to the WAStD home page.

Logins are valid for a day. Once a login has expired, you will need to login again.

Roles and permissions are allocated by adding the following groups to a User profile:

* **Data viewers** (group "data viewers") will be able to view all data owned by or shared with the User's organisation, but not edit it.
* **Data curators** (group "data curators") will be able to access the data curation and QA portal. They can edit data and assign QA trust levels.
* **Data analysts** (group "api") can find instructions how to access and authenticate against the API on their profile page. 
  They can access all data, and upload new data in bulk.

Detailed instructions for each role are available in the following chapters.

Managing access
===============
DBCA users are automatically added to the organisation "DBCA" and get the role "data viewer".

A WAStD admin manages the access permissions for a given User:

Add a User to Group "data viewers" to give them initial access to WAStD,
and add the User to their Organisation to give them visibility to all data owned by this or shared with this Organisation.
Users can be part of several Organisations, although most will belong to exactly one.

Bulk updates run by an admin on the ``./manage.py shell_plus`` on the server::

    # Add active users with a DBCA email who have logged into WAStD in the past to Group "DBCA"
    # This gives them access to DBCA data
    dbca = Organisation.objects.get(code="dbca")
    dv = Group.objects.get(name="data viewer")
    [[u.organisations.add(dbca), u.groups.add(dv)] for u in User.objects.filter(email__icontains="@dbca.wa.gov.au", is_active=True).exclude(last_login=None)]

    # Add active users who have logged into WAStD in the past to Group "data viewers"
    # This gives them access to WAStD
    [u.groups.add(dv) for u in User.objects.exclude(last_login=None).filter(is_active=True)]
