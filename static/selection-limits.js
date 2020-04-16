

function __WB_initSelectionLimit(limit) {
  // Lock Ping
  if (window.__WB_replay_top !== window) {
    return;
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    initClipBoardOverride();
  } else {
    initSelectionChangeOverride();
  }

  var alreadyRunning = false;
  var selectionChanged = false;

  function adjustSelection() {
    if (alreadyRunning) {
      return;
    }

    function sel() {
      return document.getSelection();
    }

    var string = sel().toString();

    if (string.split(" ").length <= limit) {
      return;
    }

    alreadyRunning = true;
    var direction = "forward";

    sel().modify("extend", direction, "word");
      // if selection gets bigger, reverse direction
    if (sel().toString().length >= string.length) {
      direction = "backward";
      sel().modify("extend", direction, "word");
    }
    
    string = sel().toString();

    var prevString = null;
    var count = 0;

    while (string.split(" ").length > limit) {
      prevString = string;
      sel().modify("extend", direction, "word");
      string = sel().toString();

      // if stuck of same string for some reason after >2 words, just drop out
      if (string === prevString) {
        if (++count > 2) {
          break;
        }
      } else {
        count = 0;
      }
    }

    alreadyRunning = false;
  }

  function initSelectionChangeOverride() {
    document.addEventListener("selectionchange", function (event) {
      if (alreadyRunning) {
        event.preventDefault();
        return false;
      }
      selectionChanged = true;
    });

    setInterval(function () {
      if (selectionChanged) {
        adjustSelection();
        selectionChanged = false;
      }
    }, 200);
  }

  function initClipBoardOverride() {
    function clipboardOverride(event) {
      const sel = document.getSelection().toString();
      const words = sel.split(" ");
      if (words.length <= limit) {
        return true;
      }

      event.preventDefault();
      navigator.clipboard.writeText(words.slice(0, limit).join(" ")).
        catch(function(err) {
          console.log(err);
          adjustSelection();
          if (!document.execCommand("copy")) {
            document.removeEventListener("copy", clipboardOverride);
            initSelectionChangeOverride();
          }
        });

      return false;
    };

    document.addEventListener("copy", clipboardOverride);
  }
}



