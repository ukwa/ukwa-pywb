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

    function init(bid) {
        var banner = document.createElement("wb_div", true);

        banner.setAttribute("id", bid);
        banner.setAttribute("lang", window.banner_info.locale);

        var languageOptions = [];
        if (window.banner_info.locales) {
            var locales = window.banner_info.locales;
            for(var i = 0; i < locales.length; i++) {
                var path = window.location.pathname.replace(/^\/[a-z-]{2,5}\/|^\//i, '')
                var locale = locales[i];
                languageOptions.push("<a href='/" + locale + "/" + path + "'>" + locale + "</a>");
            }
        }

        var text = "<a href='/" + (window.banner_info.locale ? window.banner_info.locale + '/' : '') + "' class='_wb_linked_logo'><img src='/static/ukwa.svg' alt='" + window.banner_info.logoAlt + "'><img src='/static/ukwa-condensed.svg' class='mobile' alt='" + window.banner_info.logoAlt + "'></a>";
        text += "<div id='_wb_capture_info'>" + window.banner_info.loadingLabel + "</div>";
        // calendar link and language switch
        text += "<div id='_wb_ancillary_links'>"+
                "<a href='" + window.banner_info.prefix + "*/" + window.activeUrl + "'><img src='/static/calendar.svg' alt='" + window.banner_info.calendarAlt + "'><span class='no-mobile'>&nbsp;" +window.banner_info.calendarLabel + "</span></a>"+
                ( languageOptions ? "<div><span class='no-mobile'>" + window.banner_info.choiceLabel + '&nbsp;</span>' + languageOptions.join(' / ') + "</div>" : '') +
                "</div>"

        banner.innerHTML = text;
        document.body.insertBefore(banner, document.body.firstChild);
    }

    function set_banner(url, ts, is_live, title) {
        var capture_str;

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

        capture_str += "<span class='_wb_catpure_date'>"+ (info_msg ? "<i>" + info_msg + "&nbsp;</i>" : "");
        capture_str += ts_to_date(ts, false);
        capture_str += "</span>";

        document.querySelector("#_wb_capture_info").innerHTML = capture_str;
    }

    if (window.top != window) {
        return;
    }

    window.addEventListener("load", function() {
        if (window.wbinfo) {
            init("_wb_plain_banner");

            set_banner(window.wbinfo.url,
                       window.wbinfo.timestamp,
                       window.wbinfo.is_live,
                       window.wbinfo.is_framed ? "" : document.title);
        } else {
            init("_wb_frame_top_banner");

            window.addEventListener("message", function(event) {
                var state = event.data;
                if (state.wb_type) {
                    set_banner(state.url, state.ts, state.is_live, state.title);
                }
            });
        }
    });

})();


