// Custom Domain Specific Fix-Up Rules Script
// ==========================================
//
// This script is injected into the replay frame after other pywb specific inserts
//
// The global "wbinfo" contains info about the current capture
// The rules can be added as follows:

//
//   if (wbinfo.url.indexOf("http://example.com/") == 0 && wbinfo.timestamp >= "2012" && navigator.userAgent.indexOf("Firefox") >= 0) {
//      //do something custom if url starts with http://example.com, timestamp >= 2012 and user agent matches Firefox
//   }
//
// This script is also injected in proxy mode. Determining if in proxy mode can be done by checking:
//
//   if (wbinfo.proxy_magic) {
//      //do something when in proxy mode
//   }
//


