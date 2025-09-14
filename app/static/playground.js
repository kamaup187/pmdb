function runDataTableEditable(tableId) {
    let table = $('#' + tableId).DataTable({
        destroy: true,
        rowId: 'stockid', // Use stockid as row identifier
        columns: [
            { data: 'stockid' },
            { data: 'date' },
            { data: 'stocktype' },
            { data: 'item' },
            { data: 'eqty' },
            {
                data: 'aqty',
                render: function(data, type, row) {
                    if (type === 'display') {
                        // Use boolean status for editability
                        let isEditable = row.status === true ? 'contenteditable="true"' : 'contenteditable="false"';
                        return `<span ${isEditable} class="editable" data-item-id="${row.stockid}">${(data || 0)}</span>`;
                    }
                    return data;
                }
            },
            {
                data: 'diff',
                render: function(data, type, row) {
                    if (type === 'display') {
                        return calculateDifference(row.eqty, row.aqty || 0);
                    }
                    return data;
                }
            },
            {
                data: 'status',
                render: function(data, type, row) {
                    if (type === 'display') {
                        // Render checkbox based on internal status
                        let checked = row.status === true ? 'checked' : '';
                        return `<input type="checkbox" class="status-checkbox" data-item-id="${row.stockid}" ${checked}>`;
                    }
                    return row.status === true; // Return boolean status
                }
            },
            { data: 'notes' }
        ],
        initComplete: function(settings, json) {
            let api = this.api();
            // Force status to boolean false for all rows
            api.rows().every(function(rowIdx) {
                let rowData = this.data();
                if (!rowData || !rowData.stockid) {
                    console.warn('Invalid row data or missing stockid:', rowData);
                    return;
                }
                rowData.status = false; // Override backend status
                this.data(rowData);
            });
            console.log('Initialized rows with status:', api.rows().data().toArray());
        },
        drawCallback: function(settings) {
            let api = this.api();

            // Debounced update function for aqty
            let updateDiff = debounce(function($cell) {
                let $row = $cell.closest('tr');
                let rowIdx = api.row($row).index();
                if (rowIdx === undefined) {
                    console.error('Row index not found for:', $row);
                    return;
                }
                let rowData = api.row(rowIdx).data();
                let newValue = parseInt($cell.text()) || 0;
                rowData.aqty = newValue;
                api.cell($row, 6).data(calculateDifference(rowData.eqty, newValue)).draw();
            }, 1500);

            // Handle input on editable aqty cells
            $('#' + tableId + ' tbody').off('input', '.editable').on('input', '.editable', function(e) {
                let $cell = $(this);
                let $row = $cell.closest('tr');
                let rowIdx = api.row($row).index();
                let rowData = api.row(rowIdx).data();
                if (rowData.status === true) {
                    updateDiff($cell);
                } else {
                    $cell.text(rowData.aqty || 0);
                    console.warn('Cannot edit aqty: status is not approved.');
                }
            });

            // Handle checkbox changes for status
            $('#' + tableId + ' tbody').off('change', '.status-checkbox').on('change', '.status-checkbox', function(e) {
                let $checkbox = $(this);
                let $row = $checkbox.closest('tr');
                let rowIdx = api.row($row).index();
                if (rowIdx === undefined) {
                    console.error('Row index not found for:', $row);
                    return;
                }
                let rowData = api.row(rowIdx).data();
                rowData.status = $checkbox.is(':checked'); // Update as boolean
                api.row(rowIdx).data(rowData);
                let $aqtyCell = $row.find('.editable');
                $aqtyCell.attr('contenteditable', rowData.status);
                console.log('Updated row status:', rowData);
                api.draw(false); // Redraw to update UI
            });
        }
    });
    return table;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Calculate difference function
function calculateDifference(eqty, aqty) {
    return (eqty || 0) - (aqty || 0);
}