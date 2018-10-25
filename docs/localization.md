## Localization/Internationalization System

The localization system uses [Babel](http://babel.pocoo.org/en/latest/) which extends the [standard Python i18n system](https://docs.python.org/3/library/gettext.html)

Babel handles the text extraction from all UI templates, sets up locale directories for translation, and compiles the locale
directories into binary files for lookup.

All localization/internationalization is kept in the [./i18n](https://github.com/ukwa/ukwa-pywb/tree/docs/i18n) directory.

### Localization Workflow

To update the translated strings, the workflow is as follows:

1) Add new text to UI templates, marked with `{% trans %}` tags or in `{{ _() }}` (See below for more info).

2) Run `./i18n/update-loc.sh` to update the translations.

3) The new text should now be in [i18n/translations/cy/LC_MESSAGES/messages.po](https://github.com/ukwa/ukwa-pywb/blob/docs/i18n/translations/cy/LC_MESSAGES/messages.po)
   
   Edit this file to provide translations.
   
4) Run `./i18n/update-loc.sh` again to update locally, OR rebuild the ukwa-pywb Docker image.

5) The newly translated strings should now be available for use and loaded in the templates.

### Localization Import/Export

To have something suitable to sent to translators, we can 

    pip install translate-toolkit

and then use `po2csv` to generate a spreadsheet for translation data entry:

    po2csv i18n/translations/cy/LC_MESSAGES/messages.po i18n/translations/cy/LC_MESSAGES/messages.csv

once we have a translation, the `csv2po` utility can be used to convert back into a `.po` file.

### Localization Setup

Babel is integrated into the `setup.py` configuration and can be run through `setup.py`.

The `en` and `cy` locales are currently configured, and correspond to language prefixes in the application.

The following scripts are provided for convenience:

- `i18n/update-loc.sh` -- extract, update and compile localization
- `i18n/clear-loc.sh` -- re-init localizations. This will clear all current translations!


### Extraction, Updates and Compilation

Babel is configured to extract text from all [Jinja2](http://jinja.pocoo.org/) [UI Templates](ui.md#ui-templates)

Babel extracts text in:
 - `{% trans %}` and `{% endtrans %}` tags
 - Inside `{{ _('text') }}` and `{{ _Q('text') }}` literals
 
 and writes them to the `./i18n/messages.pot` file.
 
This file is then copied over to:
 - For CY locale `./i18n/translations/cy/LC_MESSAGES/messages.po`
 - For EN locale `./i18n/translations/en/LC_MESSAGES/messages.po`
 
On compilation, the files are converted to binary `messages.po` -> `messages.mo`, and the binary format
is loaded at run time.
 
#### Re-Init or Add Locale
 
The `./i18n/clear-loc.sh` scripts reinits the cy and en locales, clearing all the locales.

To add a new locale, one can run: `python setup.py init_catalog -l <LOCALE>` which will set up a 
`./i18n/translations/<LOCALE>/LC_MESSAGES/messages.po` file for translations.
 
### Configuration Setup
 
To allow ukwa-pywb to find the translations, the following block must be added to the `config.yaml`:
 
```
locales_root_dir: ./i18n/translations/
locales:
  - en
  - cy
```

This setup points to the base translations directories and the locales to load.

This also enables `/en/` and `/cy/` prefixes for all collections.

### Locale Prefix and Determining Locale

The locale prefixes can be used with all collections, eg, if `/ukwa/http://example.com/` is a valid path, then so is:
- `/en/ukwa/http://example.com/`
- `/cy/ukwa/http://example.com/`

The `{{ env.pywb_lang }}` variable will be set to either: `'en'`, `'cy'`, or `''` (if no locale prefix is used).

The switch language links use the locale prefixes to switch to different locale versions.


### Note on Banner Translations

The translations in the [banner.html](https://github.com/ukwa/ukwa-pywb/blob/docs/templates/banner.html) must use the 
`decodeURIComponent("{{ _Q('text') }}")` form, which will ensure that embedded text is %-encoded on the server, and then decoded to Unicode on the client.

The reason is to avoid any non-ASCII character in the banner, since pywb intentonally does not set a charset on the top frame.

By avoiding setting the charset, pywb allows the browser to detect the charset automatically, if it is missing on the inner frame.
If a charset is set on the outer frame, the browser will assume the same charset for replay, which may not be correct.

The trade-off is that non-ASCII characters should not be added to the banner, as they will likely be decoded incorrectly.


 
 
