/*
Copyright(c) 2013-2018 Rhizome and Ilya Kreymer. Released under the GNU General Public License.

This file is part of pywb, https://github.com/webrecorder/pywb

    pywb is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pywb is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pywb.  If not, see <http://www.gnu.org/licenses/>.

*/

// Creates the default pywb banner.

(function() {
    function ts_to_date(ts, is_gmt) {
        if (!ts) {
            return "";
        }

        if (ts.length < 14) {
            ts += "00000000000000".substr(ts.length);
        }

        var datestr = (ts.substring(0, 4) + "-" +
                      ts.substring(4, 6) + "-" +
                      ts.substring(6, 8) + "T" +
                      ts.substring(8, 10) + ":" +
                      ts.substring(10, 12) + ":" +
                      ts.substring(12, 14) + "-00:00");

        var date = new Date(datestr);

        if (is_gmt) {
            return date.toGMTString();
        } else {
            return date.toLocaleString(window.banner_info.locale);
        }
    }

    function backToCalendar(evt) {
        evt.preventDefault();
        window.location = window.banner_info.prefix + "*/" + window.activeUrl;
    }

    function changeLanguage(lang, evt) {
        evt.preventDefault();
        var path = window.location.href;
        if (path.indexOf(window.banner_info.prefix) == 0) {
          path = path.substring(window.banner_info.prefix.length);
          window.location.pathname = window.banner_info.locale_prefixes[lang] + path;
        }
    }

    function init(bid) {
        var banner = document.createElement("wb_div", true);

        banner.setAttribute("id", bid);
        banner.setAttribute("lang", window.banner_info.locale);

        var logo = document.createElement("a");
        logo.setAttribute("href", "/" + (window.banner_info.locale ? window.banner_info.locale + "/" : ""));
        logo.setAttribute("class", "_wb_linked_logo");
        logo.innerHTML = "<img src='" + window.banner_info.staticPrefix + "/ukwa-2018-wob-sml.png' alt='" + window.banner_info.logoAlt + "'><img src='" + window.banner_info.staticPrefix + "/ukwa-2018-wob-sml.png' class='mobile' alt='" + window.banner_info.logoAlt + "'>";
        banner.appendChild(logo);

        var captureInfo = document.createElement("div");
        captureInfo.setAttribute("id", "_wb_capture_info");
        captureInfo.innerHTML = window.banner_info.loadingLabel;
        banner.appendChild(captureInfo);

        var ancillaryLinks = document.createElement("div");
        ancillaryLinks.setAttribute("id", "_wb_ancillary_links");

        var calendarLink = document.createElement("a");
        calendarLink.setAttribute("href", "#");
        calendarLink.addEventListener("click", backToCalendar);
        calendarLink.innerHTML = "<img src='" + window.banner_info.staticPrefix + "/calendar.svg' alt='" + window.banner_info.calendarAlt + "'><span class='no-mobile'>&nbsp;" +window.banner_info.calendarLabel + "</span>";
        ancillaryLinks.appendChild(calendarLink);

        if (typeof window.banner_info.locales !== "undefined" && window.banner_info.locales.length) {
            var locales = window.banner_info.locales;
            var languages = document.createElement("div");

            var label = document.createElement("span");
            label.setAttribute("class", "no-mobile");
            label.appendChild(document.createTextNode(window.banner_info.choiceLabel + " "));
            languages.appendChild(label);

            for(var i = 0; i < locales.length; i++) {
                var locale = locales[i];
                var langLink = document.createElement("a");
                langLink.setAttribute("href", "#");
                langLink.addEventListener("click", changeLanguage.bind(this, locale));
                langLink.appendChild(document.createTextNode(locale));

                languages.appendChild(langLink);
                if (i !== locales.length - 1) {
                    languages.appendChild(document.createTextNode(" / "));
                }
            }

            ancillaryLinks.appendChild(languages);
        }

        banner.appendChild(ancillaryLinks);

        document.body.insertBefore(banner, document.body.firstChild);
    }

    function set_banner(url, ts, is_live, title) {
        var capture_str;

        if (!url) {
            document.querySelector("#_wb_capture_info").innerHTML = window.banner_info.loadingLabel;
            return;
        }


        if (!ts) {
            return;
        }

        window.activeUrl = url;

        if (title) {
            capture_str = title;
        }  else {
            capture_str = url;
        }

        capture_str = "<b id='title_or_url' title='" + capture_str + "'>" + capture_str + "</b>";

        var info_msg;

        if (is_live) {
            info_msg = window.banner_info.LIVE_ON;
        }

        capture_str += "<span class='_wb_capture_date'>"+ (info_msg ? "<i>" + info_msg + "&nbsp;</i>" : "");
        capture_str += ts_to_date(ts, false);
        capture_str += "</span>";

        document.querySelector("#_wb_capture_info").innerHTML = capture_str;
    }

    if (window.top != window) {
        // replay frame
        function notify_unload() {
            if (window.__WB_top_frame && window.__WB_replay_top == window) {
                window.__WB_top_frame.postMessage({"wb_type": "unload"}, "*");
            }
        }

        window.addEventListener("load", function() {
            window.addEventListener("unload", notify_unload);
        });
        return;
    }

    document.addEventListener("DOMContentLoaded", function () {
        init("_wb_frame_top_banner");
    });

    window.addEventListener("load", function() {
        if (window.wbinfo) {
            set_banner(window.wbinfo.url,
                       window.wbinfo.timestamp,
                       window.wbinfo.is_live,
                       window.wbinfo.is_framed ? "" : document.title);
        } else {
            window.addEventListener("message", function(event) {
                var state = event.data;
                if (state.wb_type && state.wb_type != "unload") {
                    set_banner(state.url, state.ts, state.is_live, state.title);
                } else if (state.wb_type == "unload") {
                    set_banner(null);
                }
            });
        }
    });

})();


