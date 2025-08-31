// Updated runDataTable function
function runDataTable(tableId) {
    let table = $('#' + tableId).DataTable({
        destroy: true, // Destroy previous instance to reinitialize
        columns: [
            { data: 'stockid' },    // Item ID
            { data: 'date' },       // Date
            { data: 'stocktype' },  // Stocktake type
            { data: 'item' },       // Item name
            { data: 'eqty' },       // Expected quantity
            {
                data: 'aqty',       // Actual quantity (editable)
                render: function(data, type, row) {
                    if (type === 'display') {
                        return '<span contenteditable="true" class="editable" data-item-id="' + row.stockid + '">' + (data || 0) + '</span>';
                    }
                    return data;
                }
            },
            {
                data: 'diff',       // Difference (calculated)
                render: function(data, type, row) {
                    if (type === 'display') {
                        return calculateDifference(row.eqty, row.aqty || 0);
                    }
                    return data;
                }
            },
            { data: 'status' },     // Status
            { data: 'notes' }       // Notes
        ],
        drawCallback: function(settings) {
            let api = this.api();
            // Delegate event to table body to handle dynamically added elements
            $('#' + tableId + ' tbody').off('input', '.editable').on('input', '.editable', function(e) {
                let $cell = $(this);
                let $row = $cell.closest('tr');
                let rowIdx = api.row($row).index();
                if (rowIdx === undefined) {
                    console.error('Row index not found for:', $row);
                    return;
                }
                let rowData = api.row(rowIdx).data();
                let newValue = parseInt($cell.text()) || 0;
                rowData.aqty = newValue; // Update row data
                api.cell($row, 6).data(calculateDifference(rowData.eqty, newValue)).draw(); // Update diff column (index 6)
            });
        }
    });
    return table; // Return the instance for external use
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

// Your existing AJAX call with submit button handler
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

        $('#submitStocktakeBtn').on('click', function() {
            let stocktakeId = 1; // Replace with your actual stocktake_id
            let items = t1.rows().data().toArray().map(row => ({
                item_id: row.stockid,
                actual_count: row.aqty || 0
            }));

            $.ajax({
                url: '/stocktake/adjustments',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ stocktake_id: stocktakeId, items: items }),
                success: function(data) {
                    alert('Stocktake adjustments recorded successfully!');
                    t1.ajax.reload();
                },
                error: function(xhr) {
                    alert('Error submitting adjustments');
                }
            });
        });
    },
    error: function(xhr) {
        alert("Error");
        $("#stocktake-spinner").addClass("d-none");
    }
});

function calculateDifference(expected, actual) {
    return actual - expected;
}