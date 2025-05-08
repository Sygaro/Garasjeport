document.addEventListener("DOMContentLoaded", () => {
  const typeFilter = document.getElementById('filterType');
  const portFilter = document.getElementById('filterPort');
  const dateFromFilter = document.getElementById('filterDateFrom');
  const dateToFilter = document.getElementById('filterDateTo');
  const matchCount = document.getElementById('matchCount');
  const modalContent = document.getElementById('modalContent');
  const modal = new bootstrap.Modal(document.getElementById('logModal'));

  function applyFilter() {
    const type = typeFilter.value;
    const port = portFilter.value;
    const dateFrom = dateFromFilter.value;
    const dateTo = dateToFilter.value;

    let visibleCount = 0;
    const rows = document.querySelectorAll('#logTable tbody tr');

    rows.forEach(row => {
      const rowType = row.dataset.type;
      const rowPort = row.dataset.port;
      const rowDate = row.dataset.date;

      const matchesType = !type || rowType === type;
      const matchesPort = !port || rowPort === port;
      const matchesDateFrom = !dateFrom || (rowDate && rowDate >= dateFrom);
      const matchesDateTo = !dateTo || (rowDate && rowDate <= dateTo);

      const visible = matchesType && matchesPort && matchesDateFrom && matchesDateTo;
      row.style.display = visible ? '' : 'none';
      if (visible) visibleCount++;
    });

    matchCount.textContent = `${visibleCount} treff`;
  }

  window.resetFilters = function () {
    typeFilter.value = "";
    portFilter.value = "";
    dateFromFilter.value = "";
    dateToFilter.value = "";
    applyFilter();
  }

  window.showDetails = function (button) {
    const row = button.closest('tr');
    const raw = row.dataset.entry;
    try {
      const obj = JSON.parse(raw);
      modalContent.textContent = JSON.stringify(obj, null, 2);
    } catch (e) {
      modalContent.textContent = "Feil ved visning av detaljer.";
    }
    modal.show();
  }

  [typeFilter, portFilter, dateFromFilter, dateToFilter].forEach(el =>
    el.addEventListener('change', applyFilter)
  );

  applyFilter();
});
