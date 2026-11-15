function filterTable() {
    var filterThs = document.querySelectorAll('#ti-filter-row th');
    var tbody = document.getElementById('ti-table-body');
    var rows = tbody.getElementsByTagName('tr');

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var showRow = true;

        filterThs.forEach(function(th, index) {
            if (!showRow) return;
            var controls = th.querySelectorAll('input.filter-input, select.filter-select');
            if (!controls.length) return;
            var cells = row.getElementsByTagName('td');
            var cell = cells[index];
            if (!cell) return;
            var cellText = (cell.textContent || cell.innerText || '').toLowerCase();

            // Year-Month column: preset select + optional custom range
            if (controls.length >= 1 && controls[0].id === 'ti-month-preset') {
                var preset = controls[0].value;
                var fromVal = '', toVal = '';
                if (preset === 'custom') {
                    var fromInp = document.getElementById('ti-month-from');
                    var toInp = document.getElementById('ti-month-to');
                    fromVal = fromInp ? (fromInp.value || '') : '';
                    toVal = toInp ? (toInp.value || '') : '';
                } else if (preset === 'thismonth') {
                    var n = new Date();
                    fromVal = toVal = n.getFullYear() + '-' + String(n.getMonth()+1).padStart(2,'0');
                } else if (preset === 'lastmonth') {
                    var d2 = new Date(new Date().getFullYear(), new Date().getMonth()-1, 1);
                    fromVal = toVal = d2.getFullYear() + '-' + String(d2.getMonth()+1).padStart(2,'0');
                } else if (preset === 'last6months') {
                    var now = new Date();
                    var d3 = new Date(now.getFullYear(), now.getMonth()-5, 1);
                    fromVal = d3.getFullYear() + '-' + String(d3.getMonth()+1).padStart(2,'0');
                    toVal = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
                } else if (preset === 'thisyear') {
                    var y = new Date().getFullYear();
                    fromVal = y + '-01'; toVal = y + '-12';
                } else if (preset === 'lastyear') {
                    var y2 = new Date().getFullYear() - 1;
                    fromVal = y2 + '-01'; toVal = y2 + '-12';
                }
                // if preset is '' (All Months), fromVal/toVal stay empty -> no filter
                var parts = cellText.trim().split('-');
                var cy = (parts[0] || '').trim();
                var cm = (parts[1] || '').trim();
                var cellMonth = cy + (cm ? '-' + cm.padStart(2,'0') : '');
                if (fromVal && cellMonth < fromVal) { showRow = false; return; }
                if (toVal && cellMonth > toVal) { showRow = false; return; }
                if ((fromVal || toVal) && !cellMonth) { showRow = false; return; }
                return;
            }

            controls.forEach(function(ctrl) {
                if (!showRow) return;
                var filterValue = (ctrl.value || '').toLowerCase();
                if (filterValue && cellText.indexOf(filterValue) === -1) {
                    showRow = false;
                }
            });
        });

        row.style.display = showRow ? '' : 'none';
    }
}

