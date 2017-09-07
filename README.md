![](https://d1949u65ypatvu.cloudfront.net/static/v1434549436/img/ScrumDoSignupLogo.png)

API Version 3
=====================

This document describes the API for ScrumDo.  This is only for data hosted in the 'new' ScrumDo
that can be accessed from https://app.scrumdo.com - For API access to Classic ScrumDo (the blue
themed version) please see https://github.com/ScrumDoLLC/ScrumDoAPIV2

Authentication
--------------

We provide two methods of authenticating against the API.

### HTTP Basic
If you're creating a script that will **only be used personally or internally 
within your company**, you may use HTTP Basic authentication with your username 
and password to speed development.

A Python based example showing this can be found here:
https://github.com/ScrumDoLLC/ScrumDoAPIV3/tree/master/examples/python

### In Browser

For debugging purposes, if you make requests from your browser and are logged in, 
your session info will be carried over.  Example:
https://app.scrumdo.com/api/v3/organizations/

We do not respond with CORS headers, and we do expect a CSRF token on PUT, POST or DELETE 
so this is not a good way to authenticate for any real use.


REST
----

Our calls generally follow RESTfull principles.

POST - Creates new items
PUT - Updates existing items
GET - Retrieves data
DELETE - Removes an item

JSON
----

All of our calls return results in JSON by default.  When expecting data 
(POST or PUT), you should JSON encode your data in the body of the request.

What's a SLUG?
--------------

Projects and organizations are identified by a slug, a short string consisting of 
alpha-numeric characters or dashes.  Most other objects are identified by a numeric id.  
You can find out the slug of an organization by calling the getOrganizations call: 
https://app.scrumdo.com/api/v3/docs#!/organizations/getOrganizations_get


API Browser
-----------

You can browse all the available API calls in our interactive API Browser: 
https://app.scrumdo.com/api/v3/docs

If you are logged into ScrumDo, you will be able to actually execute API calls 
against your account via that page (ie. It's for real, be careful.) to see the inputs, 
URL's and outputs of each command.  Click the "Try it out" button under each call.

Some properties are read-only via the API.  When posting or putting data, please 
consult the body parameter of the API browser.  It lists all valid fields and gives 
examples for the format of the data expected.

![API Browser](https://raw.github.com/ScrumDoLLC/ScrumDoAPIV3/master/images/browser.png "API Browser")


Rate Throttling
---------------

GET requests - We allow up to 50 requests per 5 seconds.

POST or PUT requests - We allow up to 10 requests per 5 seconds.


Paged Results
-------------

In general, in order to make working with our API as easy as possible, we try to return 
all relevant data in a single call.  However, there are a few calls that may generate way 
too much information.  Those results will be paged.  The API Browser lists which calls will 
be paged in this way.


Subscription
------------

API access requires a premium level subscription.  If you are creating an application for public
consumption, contact us and we may be able to provide a free or low cost option.


Support
-------

All calls have at least a minimal amount of documentation in the API browser.  If anything is 
unclear, please send a message in our support email.  support@scrumdo.com

Please note - We have a limited staff able to respond to API access requests, and 
there may occasionally be a delay in a response.


Contributions
-------------

Have an example in another language, find an error in this documentation?  We'd 
love to include it, feel free to send a pull request via GitHub our way.


Older versions of the API
-------------------------

### Version 2

*Version 2* of our API should now be considered deprecated.  We will do our best to make sure it remains 
functional for at least the next 6 months (until 12/19/2015) but have no plans on maintaining it after that.  

Information on Version 2 of the API can be found here: http://www.scrumdo.com/developer/
https://www.scrumdo.com/api/v2/docs


Version 2 and Version 3 are very similar in structure, but there are some major differences to be aware of.

*Stories:*

* In general on the site we're calling them Cards instead of Stories now, but the API urls still refers to stories
* Summary, Detail, and Custom fields are all HTML formatted instead of Markdown, the old *_html fields are no longer present since they would have been redundant.
* No more category field, labels have replaced them
* No more card types, labels have replaced them
* No more status field, the cell location replaces it, see cell_id
* In addition to rank, there is now epic_rank which defines the order of the card within an epic

*Planning Poker:*

Planning poker is completely different and relies on a mix of API calls and collaboration on a 
real time channel.  Contact us if you need access here.



### Version 1

*Version 1* of our API should now be considered deprecated.  We will do our best to make sure it remains 
functional for at least the next 6 months (until 8/1/2013) but have no plans on maintaining it after that.  

Information on Version 1 of the API can be found here: http://www.scrumdo.com/developer/
