/**
 * AWS Icons for PlantUML — Icon Browser Client-Side Application
 *
 * Handles version switching (with per-version icon data rebuild),
 * category filtering via dropdown, search, clipboard copy,
 * and cross-version category resolution. All interactivity is client-side
 * DOM manipulation with no framework dependencies.
 */

/* ------------------------------------------------------------------ */
/*  State                                                              */
/* ------------------------------------------------------------------ */

/** Currently selected version string, e.g. "v23.0". */
var currentVersion = '';

/** Currently selected category (empty string = show all). */
var activeCategory = '';

/** Current search query (lowercased). */
var activeSearchQuery = '';

/* ------------------------------------------------------------------ */
/*  Cross-version category resolution  (Task 6.5)                     */
/* ------------------------------------------------------------------ */

/**
 * Resolve a category name from one version to another by walking the
 * CATEGORY_MAPPING table.
 *
 * @param {string} category  – The category name in the source version.
 * @param {string} fromVersion – Source version string.
 * @param {string} toVersion   – Target version string.
 * @returns {string|null} The resolved category name, or null if deleted.
 */
function resolveCategoryMapping(category, fromVersion, toVersion) {
  var versions = window.SUPPORTED_VERSIONS;
  var mapping  = window.CATEGORY_MAPPING;

  var fromIdx = versions.indexOf(fromVersion);
  var toIdx   = versions.indexOf(toVersion);

  if (fromIdx === -1 || toIdx === -1 || fromIdx === toIdx) {
    return category;
  }

  var resolved = category;

  if (fromIdx < toIdx) {
    for (var i = fromIdx + 1; i <= toIdx; i++) {
      var ver = versions[i];
      var entry = mapping[ver];
      if (!entry) continue;

      if (entry.deletions && entry.deletions.indexOf(resolved) !== -1) {
        return null;
      }
      if (entry.renames && entry.renames[resolved]) {
        resolved = entry.renames[resolved];
      }
    }
  } else {
    for (var i = fromIdx; i > toIdx; i--) {
      var ver = versions[i];
      var entry = mapping[ver];
      if (!entry) continue;

      if (entry.renames) {
        var keys = Object.keys(entry.renames);
        for (var j = 0; j < keys.length; j++) {
          if (entry.renames[keys[j]] === resolved) {
            resolved = keys[j];
            break;
          }
        }
      }
    }
  }

  return resolved;
}

/* ------------------------------------------------------------------ */
/*  Rebuild icon grid from per-version data                            */
/* ------------------------------------------------------------------ */

/**
 * Completely rebuild the icon grid DOM from an icon data object.
 * Creates the same structure as the Jinja2 template but dynamically.
 *
 * @param {object} iconData – The icon data dict for a version.
 * @param {string} version  – The version string for URL construction.
 */
function rebuildIconGrid(iconData, version) {
  var grid = document.querySelector('.icon-grid');
  if (!grid) return;

  // Clear existing category sections
  grid.innerHTML = '';

  var categories = iconData.categories;
  var catNames = Object.keys(categories);

  for (var i = 0; i < catNames.length; i++) {
    var catName = catNames[i];
    var cat = categories[catName];

    // Create category section
    var section = document.createElement('div');
    section.className = 'category-section';
    section.setAttribute('data-category', catName);
    section.setAttribute('data-color', cat.color);

    // Category heading
    var heading = document.createElement('h2');
    heading.className = 'category-heading';
    heading.style.borderLeftColor = cat.color;

    var nameText = document.createTextNode(catName + ' ');
    heading.appendChild(nameText);

    var countSpan = document.createElement('span');
    countSpan.className = 'category-count';
    countSpan.textContent = '(' + cat.icons.length + ')';
    heading.appendChild(countSpan);

    var colorSpan = document.createElement('span');
    colorSpan.className = 'category-color';
    colorSpan.style.color = cat.color;
    colorSpan.textContent = cat.color;
    heading.appendChild(colorSpan);

    section.appendChild(heading);

    // Icons container
    var iconsDiv = document.createElement('div');
    iconsDiv.className = 'category-icons';

    for (var j = 0; j < cat.icons.length; j++) {
      var icon = cat.icons[j];
      var baseUrl = 'https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/' + version + '/dist/';
      var pumlInclude = '!include ' + baseUrl + icon.pumlPath;

      // Create icon row
      var row = document.createElement('div');
      row.className = 'icon-row';
      row.setAttribute('data-target', icon.target);
      row.setAttribute('data-target2', icon.target2);
      row.setAttribute('data-category', catName);

      // Image
      var img = document.createElement('img');
      img.src = baseUrl + icon.pngPath;
      img.alt = icon.target + ' - ' + catName;
      img.loading = 'lazy';
      img.onerror = function() {
        this.style.display = 'none';
        this.nextElementSibling.style.display = 'flex';
      };
      row.appendChild(img);

      // Placeholder
      var placeholder = document.createElement('div');
      placeholder.className = 'icon-placeholder';
      placeholder.style.display = 'none';
      placeholder.setAttribute('aria-hidden', 'true');
      placeholder.textContent = '?';
      row.appendChild(placeholder);

      // Name
      var nameSpan = document.createElement('span');
      nameSpan.className = 'icon-name';
      nameSpan.textContent = icon.target;
      row.appendChild(nameSpan);

      // PUML path
      var code = document.createElement('code');
      code.className = 'icon-puml-path';
      code.textContent = pumlInclude;
      row.appendChild(code);

      // Copy button
      var btn = document.createElement('button');
      btn.className = 'copy-button';
      btn.textContent = 'Copy';
      btn.setAttribute('aria-label', 'Copy include statement for ' + icon.target);
      // Use a closure to capture pumlInclude
      btn.onclick = (function(text) {
        return function() { copyToClipboard(text, this); };
      })(pumlInclude);
      row.appendChild(btn);

      iconsDiv.appendChild(row);
    }

    section.appendChild(iconsDiv);
    grid.appendChild(section);
  }
}

/**
 * Simple HTML escaping for text content.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

/* ------------------------------------------------------------------ */
/*  Version switching                                                  */
/* ------------------------------------------------------------------ */

/**
 * Populate the version dropdown and set the default to the latest version.
 */
function initVersionSelector() {
  var select = document.getElementById('version-select');
  if (!select) return;

  currentVersion = select.value || window.SUPPORTED_VERSIONS[window.SUPPORTED_VERSIONS.length - 1];

  select.addEventListener('change', function () {
    var newVersion = select.value;
    switchVersion(newVersion);
  });
}

/**
 * Switch to a new version. Looks up per-version icon data from
 * ICON_DATA_BY_VERSION and rebuilds the entire icon grid.
 *
 * @param {string} version – The target version string.
 */
function switchVersion(version) {
  var oldVersion = currentVersion;
  currentVersion = version;

  // Look up per-version icon data
  var versionData = window.ICON_DATA_BY_VERSION && window.ICON_DATA_BY_VERSION[version];

  if (versionData) {
    // Rebuild the entire grid with the version's icon data
    rebuildIconGrid(versionData, version);
  } else {
    // Fallback: just update URLs in existing DOM (old behavior)
    var versionPattern = /awslabs\/aws-icons-for-plantuml\/[^/]+\/dist\//g;
    var replacement = 'awslabs/aws-icons-for-plantuml/' + version + '/dist/';

    var images = document.querySelectorAll('.icon-row img');
    for (var i = 0; i < images.length; i++) {
      var src = images[i].getAttribute('src');
      if (src) images[i].setAttribute('src', src.replace(versionPattern, replacement));
    }

    var pumlPaths = document.querySelectorAll('.icon-puml-path');
    for (var i = 0; i < pumlPaths.length; i++) {
      var text = pumlPaths[i].textContent;
      if (text) pumlPaths[i].textContent = text.replace(versionPattern, replacement);
    }
  }

  // Attempt to map active category filter through the mapping table
  if (activeCategory) {
    var resolved = resolveCategoryMapping(activeCategory, oldVersion, version);
    if (resolved === null) {
      activeCategory = '';
    } else {
      activeCategory = resolved;
    }
  }

  // Rebuild category dropdown options with correct counts for this version
  updateCategoryList(version);

  // Re-apply combined filters
  applyFilters();
}

/**
 * Rebuild the category dropdown options when the version changes.
 * Reads categories from the current DOM or from ICON_DATA_BY_VERSION.
 *
 * @param {string} version – The newly selected version.
 */
function updateCategoryList(version) {
  var select = document.getElementById('category-select');
  if (!select) return;

  // Gather categories and counts from the DOM
  var sections = document.querySelectorAll('.category-section[data-category]');
  var totalIcons = 0;

  // Clear existing options
  select.innerHTML = '';

  // Collect category info
  var catInfo = [];
  for (var i = 0; i < sections.length; i++) {
    var catName = sections[i].getAttribute('data-category');
    var iconCount = sections[i].querySelectorAll('.icon-row').length;
    totalIcons += iconCount;
    catInfo.push({ name: catName, count: iconCount });
  }

  // Add "All Categories" option
  var allOption = document.createElement('option');
  allOption.value = 'all';
  allOption.textContent = 'All Categories (' + totalIcons + ')';
  select.appendChild(allOption);

  // Add per-category options
  for (var i = 0; i < catInfo.length; i++) {
    var option = document.createElement('option');
    option.value = catInfo[i].name;
    option.textContent = catInfo[i].name + ' (' + catInfo[i].count + ')';
    select.appendChild(option);
  }

  // Restore selection
  if (activeCategory) {
    select.value = activeCategory;
    // If the category doesn't exist in the new version, reset to all
    if (select.value !== activeCategory) {
      activeCategory = '';
      select.value = 'all';
    }
  } else {
    select.value = 'all';
  }
}

/* ------------------------------------------------------------------ */
/*  Category filtering via dropdown                                    */
/* ------------------------------------------------------------------ */

/**
 * Initialize category dropdown and attach change listener.
 */
function initCategoryFilter() {
  var select = document.getElementById('category-select');
  if (!select) return;

  select.addEventListener('change', onCategoryChange);
}

/**
 * Handler for category dropdown changes.
 */
function onCategoryChange() {
  var select = document.getElementById('category-select');
  if (!select) return;

  var value = select.value;
  activeCategory = (value === 'all') ? '' : value;
  applyFilters();
}

/**
 * Show/hide category sections based on the selected category.
 * When activeCategory is empty, all categories are shown.
 *
 * @param {string} category – Category name to show, or empty for all.
 */
function filterByCategory(category) {
  var sections = document.querySelectorAll('.category-section[data-category]');
  for (var i = 0; i < sections.length; i++) {
    var cat = sections[i].getAttribute('data-category');
    if (!category || category === cat) {
      sections[i].style.display = '';
    } else {
      sections[i].style.display = 'none';
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Search                                                             */
/* ------------------------------------------------------------------ */

/**
 * Attach an input listener to the search bar.
 */
function initSearch() {
  var input = document.getElementById('search-input');
  if (!input) return;

  input.addEventListener('input', function () {
    activeSearchQuery = input.value.toLowerCase();
    applyFilters();
  });
}

/**
 * Filter individual icon rows by search query. Matches against
 * data-target and data-target2 attributes (case-insensitive).
 *
 * @param {string} query – Lowercased search string.
 */
function filterBySearch(query) {
  var rows = document.querySelectorAll('.icon-row');
  for (var i = 0; i < rows.length; i++) {
    var target  = (rows[i].getAttribute('data-target')  || '').toLowerCase();
    var target2 = (rows[i].getAttribute('data-target2') || '').toLowerCase();

    if (!query || target.indexOf(query) !== -1 || target2.indexOf(query) !== -1) {
      rows[i].style.display = '';
    } else {
      rows[i].style.display = 'none';
    }
  }
}

/**
 * Combine active category filter and search query to determine final
 * visibility of category sections and individual icon rows.
 */
function applyFilters() {
  // First: show/hide category sections
  filterByCategory(activeCategory);

  // Second: within visible sections, show/hide individual rows by search
  filterBySearch(activeSearchQuery);

  // If search is active, also hide category sections that have zero visible rows
  if (activeSearchQuery) {
    var sections = document.querySelectorAll('.category-section[data-category]');
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].style.display === 'none') continue;

      var allRows = sections[i].querySelectorAll('.icon-row');
      var hasVisible = false;
      for (var j = 0; j < allRows.length; j++) {
        if (allRows[j].style.display !== 'none') {
          hasVisible = true;
          break;
        }
      }
      if (!hasVisible) {
        sections[i].style.display = 'none';
      }
    }
  }

  // Update icon counts
  updateIconCounts();
}

/* ------------------------------------------------------------------ */
/*  Clipboard copy & icon counts                                       */
/* ------------------------------------------------------------------ */

/**
 * Copy text to the clipboard. Uses the modern Clipboard API with a
 * fallback to document.execCommand('copy') via a temporary textarea.
 *
 * @param {string} text   – The text to copy.
 * @param {HTMLElement} button – The copy button element for feedback.
 */
function copyToClipboard(text, button) {
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
 * @param {string} text   – The text to copy.
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
    var success = document.execCommand('copy');
    if (success) {
      showCopyConfirmation(button);
    } else {
      selectTextForManualCopy(button);
    }
  } catch (e) {
    selectTextForManualCopy(button);
  }

  document.body.removeChild(textarea);
}

/**
 * If both clipboard methods fail, select the PUML path text so the
 * user can manually copy it.
 *
 * @param {HTMLElement} button – The copy button element.
 */
function selectTextForManualCopy(button) {
  var row = button.closest('.icon-row');
  if (!row) return;

  var codeEl = row.querySelector('.icon-puml-path');
  if (!codeEl) return;

  var range = document.createRange();
  range.selectNodeContents(codeEl);
  var sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
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
 * Update the visible and total icon count displays,
 * and update per-category filtered counts in headings.
 */
function updateIconCounts() {
  var allRows = document.querySelectorAll('.icon-row');
  var totalCount = allRows.length;
  var visibleCount = 0;

  for (var i = 0; i < allRows.length; i++) {
    var row = allRows[i];
    var section = row.closest('.category-section');
    if (row.style.display !== 'none' && section && section.style.display !== 'none') {
      visibleCount++;
    }
  }

  var visibleEl = document.getElementById('visible-count');
  var totalEl   = document.getElementById('total-count');

  if (visibleEl) visibleEl.textContent = visibleCount;
  if (totalEl)   totalEl.textContent   = totalCount;

  // Update per-category counts in headings
  var sections = document.querySelectorAll('.category-section[data-category]');
  for (var i = 0; i < sections.length; i++) {
    var sectionRows = sections[i].querySelectorAll('.icon-row');
    var sectionTotal = sectionRows.length;
    var sectionVisible = 0;
    for (var j = 0; j < sectionRows.length; j++) {
      if (sectionRows[j].style.display !== 'none') {
        sectionVisible++;
      }
    }
    var countSpan = sections[i].querySelector('.category-count');
    if (countSpan) {
      if (activeSearchQuery && sectionVisible !== sectionTotal) {
        countSpan.textContent = '(' + sectionVisible + ' of ' + sectionTotal + ')';
      } else {
        countSpan.textContent = '(' + sectionTotal + ')';
      }
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Initialization                                                     */
/* ------------------------------------------------------------------ */

document.addEventListener('DOMContentLoaded', function () {
  initVersionSelector();
  initCategoryFilter();
  initSearch();
  updateIconCounts();
});
