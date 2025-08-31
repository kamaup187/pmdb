// Updated runDataTable function
function runDataTable(tableId) {
    let table = $('#' + tableId).DataTable({
        destroy: true,
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
                        return '<span contenteditable="true" class="editable" data-item-id="' + row.stockid + '">' + (data || 0) + '</span>';
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
            { data: 'status' },
            { data: 'notes' }
        ],
        drawCallback: function(settings) {
            let api = this.api();
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
            }, 300);

            $('#' + tableId + ' tbody').off('input', '.editable').on('input', '.editable', function(e) {
                let $cell = $(this);
                updateDiff($cell);
            });
        }
    });
    return table;
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Updated addStocktakeToTable function
function addStocktakeToTable(data, table) {
    table.clear();

    let tableData = data.map(item => ({
        stockid: item.stockid,
        date: item.date,
        stocktype: item.stocktype,
        item: item.item,
        eqty: item.eqty || 0,
        aqty: item.aqty || 0,
        diff: item.diff || 0,
        status: item.status,
        notes: item.notes
    }));

    table.rows.add(tableData).draw();
}

// New initSubmitHandler function
function initSubmitHandler(table) {
    $('#submitStocktakeBtn').off('click').on('click', function() {
        if (!confirm('Are you sure you want to submit these adjustments? This will create new stock transaction entries.')) {
            return;
        }

        let stocktakeId = window.stocktakeId || 1; // Use a global or fallback (define stocktakeId elsewhere)
        let initialData = table.rows().data().toArray();
        let items = table.rows().data().toArray().map(row => ({
            item_id: row.stockid,
            actual_count: row.aqty || 0
        }));

        let hasChanges = initialData.some((row, index) => {
            let newRow = table.row(index).data();
            return newRow.aqty !== initialData[index].aqty;
        });

        if (!hasChanges) {
            alert('No changes detected. Please edit at least one Actual Qty before submitting.');
            return;
        }

        $.ajax({
            url: '/stocktake/adjustments',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ stocktake_id: stocktakeId, items: items }),
            success: function(data) {
                alert('Stocktake adjustments recorded successfully!');
                table.ajax.reload();
            },
            error: function(xhr) {
                alert('Error submitting adjustments');
            }
        });
    });
}

// Updated AJAX call
$(document).ready(function() {
    $.ajax({
        url: "/v2/stock/takes",
        type: "get",
        data: {
            target: "all"
        },
        success: function(response) {
            renderStocktakeTemplate("allStocktakeTable", $("#stocktake-all-table"));
            var t1 = runDataTable("allStocktakeTable");
            addStocktakeToTable(response[0], t1);
            $("#stocktake-spinner").addClass("d-none");

            // Set stocktakeId if available in response
            window.stocktakeId = response[0].stocktake_id || 1; // Store globally or adjust logic
            initSubmitHandler(t1); // Initialize submit handler with t1
        },
        error: function(xhr) {
            alert("Error");
            $("#stocktake-spinner").addClass("d-none");
        }
    });
});

function calculateDifference(expected, actual) {
    return actual - expected;
}