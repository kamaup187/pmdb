// Datatable update
function updateDataTable(data,table) {
    // Assuming data is an array of objects
    // var table = $('#primaryData').DataTable();

    // Clear the existing data
    table.clear();

    // Add new data
    data.forEach(function(item) {

        table.row.add([
            item.id,             // PNo
            item.branch,           // Name
            item.date,        // Region
            item.amount,            // Phone
            item.status,       // Branch
            '<button class="btn btn-light btn-sm delete" data-id="' + item.id + '">View</button>'  // Remove button
        ]);
    });

    // Draw the updated table
    table.draw();
}


function updateRoleDataTable(data,table) {
    table.clear();
    data.forEach(function(item) {
        table.row.add([
            item.id,             // PNo
            item.name,           // Name
            item.desc,        // Region
            '<button class="btn btn-light btn-sm delete" data-id="' + item.id + '">View</button>'  // Remove button
        ]);
    });
    table.draw();
}

function updateUserDataTable(data,table) {
    table.clear();
    data.forEach(function(item) {
        table.row.add([
            item.id,             // PNo
            item.code,           // Name
            item.name,        // Region
            item.branch,
            item.tel,
            item.role,
            item.status,       // Branch
            '<button class="btn btn-light btn-sm delete" data-id="' + item.id + '">View</button>'  // Remove button
        ]);
    });
    table.draw();
}


//TABLES TEMPLATES GOES HERE
var dataTableTemplate = `
<table id="primaryData" class="table shadow table-bordered table-bordered-rows table-striped mb-1" width="100%" cellspacing="0">
    <thead class="custom-header">
        <tr>
            <th class="fw-bold">Id</th>
            <th class="fw-bold">Location</th>
            <th class="fw-bold">Date</th>
            <th class="fw-bold">Attendees</th>
            <th class="fw-bold">Status</th>
            <th class="fw-bold">Action</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>

`
var roleDataTableTemplate = `
<table id="primaryData" class="table shadow table-bordered table-bordered-rows table-striped mb-1" width="100%" cellspacing="0">
    <thead class="custom-header">
        <tr>
            <th class="fw-bold">Code</th>
            <th class="fw-bold">Name</th>
            <th class="fw-bold">Desc</th>
            <th class="fw-bold">Action</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>

`
var userDataTableTemplate = `
<table id="primaryData" class="table shadow table-bordered table-bordered-rows table-striped mb-1" width="100%" cellspacing="0">
    <thead class="custom-header">
        <tr>
            <th class="fw-bold">#</th>
            <th class="fw-bold">Code</th>
            <th class="fw-bold">Name</th>
            <th class="fw-bold">Address</th>
            <th class="fw-bold">Contact</th>
            <th class="fw-bold">Role</th>
            <th class="fw-bold">Status</th>
            <th class="fw-bold">Action</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>

`

var cashTemplate = `
		
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">Meetings & Events</h1>
</div>
<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#requestModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    Create new event
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="requests-table-tab" class="requests-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="requests-all-tab" data-bs-toggle="tab" href="#requests-all" role="tab" aria-controls="requests-all" aria-selected="true">All</a>
<a class="flex-sm-fill text-sm-center nav-link"  id="requests-pending-tab" data-bs-toggle="tab" href="#requests-pending" role="tab" aria-controls="requests-pending" aria-selected="false">Past</a>
<a class="flex-sm-fill text-sm-center nav-link" id="requests-accepted-tab" data-bs-toggle="tab" href="#requests-accepted" role="tab" aria-controls="requests-accepted" aria-selected="false">Current</a>
<a class="flex-sm-fill text-sm-center nav-link" id="requests-delivered-tab" data-bs-toggle="tab" href="#requests-delivered" role="tab" aria-controls="requests-delivered" aria-selected="false">Upcoming</a>
</nav>



<div class="tab-content" id="requests-table-tab-content">

    <div id="requests-spinner" class="d-flex justify-content-center d-none">
        <div class="spinner-border text-success m-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="tab-pane fade" id="requests-pending" role="tabpanel" aria-labelledby="requests-pending-tab">
        <div class="app-card app-card-requests-table shadow-sm mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="requests-pending-table" class="table-responsive">
                        </div>
                    </div>
                </div>
            
            </div><!--//app-card-body-->		
        </div><!--//app-card-->						
    </div><!--//tab-pane-->

    <div class="tab-pane fade" id="requests-accepted" role="tabpanel" aria-labelledby="requests-accepted-tab">
        <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="requests-accepted-table" class="table-responsive">
                        </div>
                    </div>
                </div>

            </div><!--//app-card-body-->		
        </div><!--//app-card-->
    </div><!--//tab-pane-->

    <div class="tab-pane fade" id="requests-delivered" role="tabpanel" aria-labelledby="requests-delivered-tab">
        <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="requests-delivered-table" class="table-responsive">
                        </div>
                    </div>
                </div>

            </div><!--//app-card-body-->		
        </div><!--//app-card-->
    </div><!--//tab-pane-->

    <div class="tab-pane fade show active" id="requests-all" role="tabpanel" aria-labelledby="requests-all-tab">
        <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="requests-all-table" class="table-responsive">
                        </div>
                    </div>
                </div>

            </div><!--//app-card-body-->		
        </div><!--//app-card-->
    </div><!--//tab-pane-->
</div><!--//tab-content-->
`


var floatTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">Activities</h1>
</div>
<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#"  data-bs-toggle="modal" data-bs-target="#floatModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    Create an activity
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="floats-table-tab" class="floats-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="floats-all-tab" data-bs-toggle="tab" href="#floats-all" role="tab" aria-controls="floats-all" aria-selected="true">All activities</a>
<a class="flex-sm-fill text-sm-center nav-link" id="floats-pending-tab" data-bs-toggle="tab" href="#floats-pending" role="tab" aria-controls="floats-pending" aria-selected="false">Past activities</a>
<a class="flex-sm-fill text-sm-center nav-link" id="floats-confirmed-tab" data-bs-toggle="tab" href="#floats-confirmed" role="tab" aria-controls="floats-confirmed" aria-selected="false">Upcoming activities</a>
</nav>


<div class="tab-content" id="floats-table-tab-content">

    <div id="floats-spinner" class="d-flex justify-content-center d-none">
        <div class="spinner-border text-success m-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="tab-pane fade" id="floats-pending" role="tabpanel" aria-labelledby="floats-pending-tab">
        <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="floats-pending-table" class="table-responsive">
                        </div>
                    </div>
                </div>

            </div><!--//app-card-body-->		
        </div><!--//app-card-->					
    </div><!--//tab-pane-->


    <div class="tab-pane fade" id="floats-confirmed" role="tabpanel" aria-labelledby="floats-confirmed-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="floats-confirmed-table" class="table-responsive">
                            </div>
                        </div>
                    </div>

                </div><!--//app-card-body-->		
            </div><!--//app-card-->	
    </div><!--//tab-pane-->

    <div class="tab-pane fade show active" id="floats-all" role="tabpanel" aria-labelledby="floats-all-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="floats-all-table" class="table-responsive">
                            </div>
                        </div>
                    </div>

                </div><!--//app-card-body-->		
            </div><!--//app-card-->	
    </div><!--//tab-pane-->
</div><!--//tab-content-->
`

var roleTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">User Roles & Permissions</h1>
</div>
<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#roleModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    New role
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->


<div class="tab-content">
    <div id="roles-spinner" class="d-flex justify-content-center d-none">
        <div class="spinner-border text-success m-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="tab-pane fade show active" id="roles-all" role="tabpanel">
                <div class="app-card app-card-requests-table mb-5">
                    <div class="app-card-body">
                        <div class="row">
                            <div class="col-lg-12 no-padding">
                                <div id="roles-all-table" class="table-responsive">
                                </div>
                            </div>
                        </div>

                    </div><!--//app-card-body-->		
                </div><!--//app-card-->						
    </div><!--//tab-pane-->
</div>

`
var userTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">User Management</h1>
</div>
<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto d-none">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#userModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    New user
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<div class="tab-content" id="users-table-tab-content">

    <div id="users-spinner" class="d-flex justify-content-center d-none">
        <div class="spinner-border text-success m-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="tab-pane fade show active" id="users-all" role="tabpanel" aria-labelledby="users-all-tab">
            <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="users-all-table" class="table-responsive">
                        </div>
                    </div>
                </div>
            </div><!--//app-card-body-->		
        </div><!--//app-card-->						
    </div><!--//tab-pane-->
</div>

`
var attendanceTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">Attendance</h1>
</div>
<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#">
                    <i data-feather="log-in" style="width: 16px; height: 16px;"></i>
                    Check in
                </a>
                <a class="btn app-btn-secondary" href="#">
                    <i data-feather="log-out" style="width: 16px; height: 16px;"></i>
                    Check out
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->
<p class="fst-italic">Coming soon</p>
`
var logsTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">User Logs</h1>
</div>
</div><!--//row-->
<p class="fst-italic">Coming soon</p>
`

