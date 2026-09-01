/**
 * AWS Icons for PlantUML — Examples Page Client-Side Application
 *
 * Handles the "Example" dropdown selector: showing/hiding the pre-rendered
 * example panels (source text + rendered images), and copying example source
 * to the clipboard. All interactivity is client-side DOM manipulation with no
 * framework dependencies.
 */

/* ------------------------------------------------------------------ */
/*  Example selection                                                  */
/* ------------------------------------------------------------------ */

/**
 * Show the example panel matching the given index and hide all others.
 *
 * @param {string} index – The zero-based example index (as a string).
 */
function showExample(index) {
  var panels = document.querySelectorAll('.example-panel');
  for (var i = 0; i < panels.length; i++) {
    if (panels[i].getAttribute('data-index') === index) {
      panels[i].hidden = false;
    } else {
      panels[i].hidden = true;
    }
  }
}

/**
 * Initialize the example dropdown and attach a change listener.
 * Falls back to the first example if the selector has no value.
 */
function initExampleSelector() {
  var select = document.getElementById('example-select');
  if (!select) return;

  showExample(select.value || '0');

  select.addEventListener('change', function () {
    showExample(select.value);
  });
}

/* ------------------------------------------------------------------ */
/*  Clipboard copy                                                     */
/* ------------------------------------------------------------------ */

/**
 * Copy text to the clipboard. Uses the modern Clipboard API with a
 * fallback to document.execCommand('copy') via a temporary textarea.
 *
 * @param {string} text – The text to copy.
 * @param {HTMLElement} button – The copy button element for feedback.
 */
function copyText(text, button) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function () {
      showCopyConfirmation(button);
    }).catch(function () {
      fallbackCopy(text, button);
    });
  } else {
    fallbackCopy(text, button);
  }
}

/**
 * Fallback copy using a temporary textarea and execCommand.
 *
 * @param {string} text – The text to copy.
 * @param {HTMLElement} button – The copy button element for feedback.
 */
function fallbackCopy(text, button) {
  var textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();

  try {
    document.execCommand('copy');
    showCopyConfirmation(button);
  } catch (e) {
    /* no-op: leave the user to copy manually */
  }

  document.body.removeChild(textarea);
}

/**
 * Show brief visual confirmation on the copy button.
 *
 * @param {HTMLElement} button – The copy button element.
 */
function showCopyConfirmation(button) {
  var originalText = button.textContent;
  button.textContent = 'Copied!';
  button.classList.add('copied');

  setTimeout(function () {
    button.textContent = originalText;
    button.classList.remove('copied');
  }, 1500);
}

/**
 * Attach click listeners to every copy button. Each button references the
 * id of the <code> element holding the source via data-copy-target.
 */
function initCopyButtons() {
  var buttons = document.querySelectorAll('.copy-button[data-copy-target]');
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function () {
      var targetId = this.getAttribute('data-copy-target');
      var codeEl = document.getElementById(targetId);
      if (codeEl) {
        copyText(codeEl.textContent, this);
      }
    });
  }
}

/* ------------------------------------------------------------------ */
/*  Initialization                                                     */
/* ------------------------------------------------------------------ */

document.addEventListener('DOMContentLoaded', function () {
  initExampleSelector();
  initCopyButtons();
});
