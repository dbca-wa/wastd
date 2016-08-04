Overview
========

This chapter gives a quick overview of the WA Stranding Database WAStD.

**Disclaimer** WAStD is currently in the proof of concept (POC) phase, and not a
production system. This documentation will evlove along with the software
and may pre-empt future development.

WAStD is a data clearinghouse for:

* Turtle strandings in WA, as reported to the Department of Parks & Wildlife, WA.

WAStD is built scalable enough to accommodate other, related, data:

* Cetacean and pinniped strandings
* Turtle tagging observations, taken of nesting turtles
* Turtle track observations, taken at sunrise after nesting (nests and false crawls)

WAStD offers as main functionalities:

* A "backstage" area, through which trained and trusted data curators can enter
  data from paper data sheets, then proofread and QA the data.
* A landing page with an interactive map displaying the data (coming up: filters
  to restrict the data shown, export tools).
* A RESTful API that allows authenticated users to create, update, and download
  the data.

WAStD will integrate in the Departmental information landscape as follows:

* Legacy data (starting with Turtle strandings) is manually entered from paper forms.
* Legacy data that lives in ageing systems can (if desired) be batch-uploaded to WAStD.
* WAStD can batch-upload its data to corporate data warehouses, once they exist (e.g. BioSys).
* Analytical applications anwering defined management questions (informing
  monitoring reports, ministerial inquries, conservation planning decisions) can be
  built right now consuming the WAStD API, and later refactored to consume data from
  departmental data warehouses, once these become the point of truth for the data.
