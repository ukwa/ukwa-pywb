(function() {
  var loaded = false;

  document.addEventListener("readystatechange", function() {
    if (document.readyState === "complete") {
      if (!loaded) {
        loadTransclusions();
        loaded = true;
      }
    }
  });

  function loadTransclusions() {
    var viUrl = window.location.href.replace("mp_", "vi_");

    window.fetch(viUrl)
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        addTransclusions(json);
      })
      .catch(function(err) {
      });
  }

  function addTransclusions(json) {
    var selector = json.selector || "object, embed";
    var result = document.querySelector(selector);
    if (!result) {
      console.warn("No target to add video transclusions");
      return;
    }

    var parentElem = result.parentElement;

    if (!json.formats) {
      console.warn("No formats to add!");
      return;
    }

    var video = document.createElement("video");
    video.setAttribute("controls", "true");
    video.setAttribute("style", "width: 100%; height: 100%");
    //video.setAttribute("autoplay", "true");
    //video.setAttribute("muted", true);

    video.oncanplaythrough = function() {
        if (!video.hasStarted) {
          video.muted = true;
          video.hasStarted = true;
        }
        video.play();
    }

    json.formats.forEach(function(data) {
      if (data.skip_as_source) {
        return;
      }
      var source = document.createElement("source");
      source.src = data.url;
      if (data.mime) {
        source.type = data.mime;
      }
      video.appendChild(source);
    });

    parentElem.replaceChild(video, result);
  }

})();

