## ukwa-pywb Custom UI

The standard UI for pywb is extended to provide a UKWA header on most pages, and a UKWA themed banner.

Additionally, links to calendar page and locale switching are provided on all UI pages.

### UI Templates

The follow UI templates are provided in the [templates](https://github.com/ukwa/ukwa-pywb/tree/master/templates) directory.
The templates use the [Jinja2](http://jinja.pocoo.org/) templating system.

- `banner.html` - The main banner inserted into the replay top frame. Most of the banner is created dynamically through the included default_banner.js file.

- `base.html` -- Base UI template, providing the UKWA header

- `error.html` -- Main error page which is displayed for all errors, except resource not found. Contains different messages based on status code.

- `frame_insert.html` -- The top-level frame that contains the replay frame.

- `index.html` -- The home page.

- `locks.html` -- The [Admin Locks Page](locks.md#admin-page-and-api)

- `not_found.html` -- The error page for 'resource not found' error when a resource is not in the archive.

- `query.html` -- The calendar page. The actual calendar is constructed client-side via included `query.js` by querying the CDX server via an ajax request.

- `search.html` -- The collection search page. Contains a search bar to search the collection by URL.


The text in all of the templates is [extracted for localization](https://github.com/ukwa/ukwa-pywb/blob/docs/docs/localization.md#extraction-updates-and-compilation)

### Static Files

Most of the static file assets are found in the `static` directory, and additional assets served from the base `pywb` package.

These static assets can be served by nginx in production. See [Nginx Deployment](deployment.md#running-behind-nginx) for more info.
