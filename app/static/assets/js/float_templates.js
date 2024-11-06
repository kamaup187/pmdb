function toggleSide(){
    var isMobile = false; //initiate as false
    // device detection
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) { 
        isMobile = true;
    }
  
    return isMobile
  }


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
            item.status,
            item.posted_by,       // Branch
            item.collectedby,       // Branch

            // Branch
            '<button class="btn btn-light btn-sm update-request-button" data-id="' + item.id + '" data-bs-toggle="modal" data-bs-target="#updateRequestModal">View</button>'  // Remove button
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
            '<button class="btn btn-light btn-sm update-role-button" data-id="' + item.id + '" data-bs-toggle="modal" data-bs-target="#updateRoleModal">View</button>',  // Remove button
            item.name,           // Name
            item.desc,        // Region
        ]);
    });
    table.draw();
}

function updateFloatDataTable(data,table) {
    table.clear();
    data.forEach(function(item) {
        table.row.add([
            item.id,
            item.branch,             // PNo
            item.date,           // Name
            item.amount,        // Region
            item.status,
            item.postedby,
            item.collectedby,
            '<button class="btn btn-light btn-sm update-float-button" data-id="' + item.id + '" data-bs-toggle="modal" data-bs-target="#updateFloatModal">View</button>'  // Remove button
        ]);
    });
    table.draw();
}

function updateUserDataTable(data,table) {
    table.clear();
    data.forEach(function(item) {
        table.row.add([
            item.id,             // PNo
            '<button class="btn btn-light btn-sm update-user-button" data-id="' + item.id + '" data-bs-toggle="modal" data-bs-target="#updateUserModal">View</button>',  // Remove button
            item.code,           // Name
            item.name,        // Region
            item.branch,
            item.tel,
            item.role,
            item.status,
        ]);
    });
    table.draw();
}

function updateAccountDataTable(data,table) {
    table.clear();
    data.forEach(function(item) {
        table.row.add([
            item.name,             // PNo
            '<button class="btn btn-light btn-sm update-account-button" data-id="' + item.id + '" data-bs-toggle="modal" data-bs-target="#updateAccountModal">View</button>',  // Remove button
            item.ob,           // Name
            item.cb,        // Region
            item.limit,
            item.status,
            item.ltd,
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
            <th class="fw-bold">Branch</th>
            <th class="fw-bold">Date</th>
            <th class="fw-bold">Amount</th>
            <th class="fw-bold">Status</th>
            <th class="fw-bold">PostedBy</th>
            <th class="fw-bold">CollectedBy</th>
            <th class="fw-bold">Action</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>

`
var floatDataTableTemplate = `
<table id="primaryData" class="table shadow table-bordered table-bordered-rows table-striped mb-1" width="100%" cellspacing="0">
    <thead class="custom-header">
        <tr>
            <th class="fw-bold">Id</th>
            <th class="fw-bold">Branch</th>
            <th class="fw-bold">Date</th>
            <th class="fw-bold">Amount</th>
            <th class="fw-bold">Status</th>
            <th class="fw-bold">PostedBy</th>
            <th class="fw-bold">CollectedBy</th>
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
            <th class="fw-bold">Action</th>
            <th class="fw-bold">Name</th>
            <th class="fw-bold">Access</th>
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
            <th class="fw-bold">Action</th>
            <th class="fw-bold">Code</th>
            <th class="fw-bold">Name</th>
            <th class="fw-bold">Branch</th>
            <th class="fw-bold">Contact</th>
            <th class="fw-bold">Role</th>
            <th class="fw-bold">Status</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>
`

var accountDataTableTemplate = `
<table id="primaryData" class="table shadow table-bordered table-bordered-rows table-striped mb-1" width="100%" cellspacing="0">
    <thead class="custom-header">
        <tr>
            <th class="fw-bold">Acc#</th>
            <th class="fw-bold">Action</th>
            <th class="fw-bold">Op.Bal</th>
            <th class="fw-bold">Curr.Bal</th>
            <th class="fw-bold">Limit</th>
            <th class="fw-bold">Status</th>
            <th class="fw-bold">L.T.D</th>
        </tr>
    </thead>
    <tbody>
        <!-- Populate dynamically -->
    </tbody>
</table>
`

var roleUpdateForm = (roleobj,roles) => {
    console.log("perms", roles)
    
    return `

                <div class="row g-4 settings-section">
	                <div class="col-12 col-md-4">
		                <h3 class="section-title">Update Role</h3>
		                <div class="section-intro">Modify/change role permissions</div>
	                </div>
	                <div class="col-12 col-md-8">
		                <div class="app-card app-card-modal app-card-settings shadow-sm p-4">
						    
						    <div class="app-card-body">
							    <form class="settings-form">
								    <div class="mb-3">
									    <label for="role-update-name" class="form-label">Change role name<span class="ms-2" data-bs-container="body" data-bs-toggle="popover" data-bs-trigger="hover focus"  data-bs-placement="top" data-bs-content="Role name"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
  <path d="M8.93 6.588l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588z"/>
  <circle cx="8" cy="4.5" r="1"/>
</svg></span></label>
									    <input type="text" class="form-control" id="role-update-name" value="${roleobj.name}" required>
									</div>

                                    <input type="hidden" class="form-control" id="role-update-id" value="${roleobj.id}">


							    </form>
						    </div><!--//app-card-body-->
						    
						</div><!--//app-card-->
	                </div>
                </div><!--//row-->

				


                <hr class="my-4">
                <div class="row g-4 settings-section">
	                <div class="col-12 col-md-4">
		                <h3 class="section-title">Permissions</h3>
		                <div class="section-intro">Update permissions</div>
	                </div>
	                <div class="col-12 col-md-8">
		                <div class="app-card app-card-modal app-card-settings shadow-sm p-4">						    
						    <div class="app-card-body">
							    <form class="settings-form scrollable">
                                    ${roles.map(permission => `
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="permission-${permission.id}" ${permission.active ? 'checked' : ''}>
                                            <label class="form-check-label" for="permission-${permission.id}">${permission.name}</label>
                                        </div>
                                    `).join('')}
							    </form>
						    </div><!--//app-card-body-->						    
						</div><!--//app-card-->
	                </div>
                </div><!--//row-->

                <div>
                <button id="update-role-btn" type="button" class="btn app-btn-primary" >Submit</button>
                </div>

                <hr class="my-4">



`;
    };


    var userUpdateForm = (memberobj,rolesArray,branchesArray) => {

        const roleOptions = rolesArray.map(r => `
            <option value="${r.value}" ${r.value === memberobj.role ? 'selected' : ''}>${r.label}</option>
        `).join('');

        const branchOptions = branchesArray.map(r => `
            <option value="${r.value}" ${r.value === memberobj.branch ? 'selected' : ''}>${r.label}</option>
        `).join('');
        
        return `
    
    
    
                                    <form class="settings-form">
                                        <div class="mb-3">
                                            <label for="user-update-name" class="form-label">Update Name<span class="ms-2" data-bs-container="body" data-bs-toggle="popover" data-bs-trigger="hover focus"  data-bs-placement="top" data-bs-content="Full name"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
      <path d="M8.93 6.588l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588z"/>
      <circle cx="8" cy="4.5" r="1"/>
    </svg></span></label>
                                            <input type="text" class="form-control" id="user-update-name" value="${memberobj.name}" required>
                                        </div>
                                        <div class=row>
                                            <div class="col-6 mb-3">
                                                <label for="user-update-mobile" class="form-label">Update contact</label>
                                                <input type="text" class="form-control" id="user-update-mobile" value="${memberobj.tel}" required>
                                            </div>

                                            <div class="col-6 mb-3">
                                                <label for="user-update-staff" class="form-label">Update staffId</label>
                                                <input type="text" class="form-control" id="user-update-staff" value="${memberobj.code}" required>
                                            </div>
                                        </div>
    
                                        <div class="mb-3 row">
                                            <div class="col-6">
                                                <label for="user-update-pass1" class="form-label">Update password</label>
                                                <input type="password" class="form-control" id="user-update-pass1" placeholder="******">
                                            </div>
                                            <div class="col-6">
                                                <label for="user-update-pass2" class="form-label">Confirm password</label>
                                                <input type="password" class="form-control" id="user-update-pass2" placeholder="******">
                                            </div>
                                        </div>
    
                                        <input type="hidden" class="form-control" id="user-update-id" value="${memberobj.id}">
    
                                        <div class="mb-3 row">
                                            <div class="col-6">
                                                <label for="user-update-role" class="form-label">Update role</label>
                                                <select class="form-select" id="user-update-role">
                                                    <option selected disabled value="">Select role</option>
                                                    ${roleOptions}
                                              </select>
                                            </div>
                                            <div class="col-6">
                                                <label for="user-update-branch" class="form-label">Update branch</label>
                                                <select class="form-select" id="user-update-branch">
                                                    <option selected disabled value="">Select branch</option>
                                                    ${branchOptions}
                                              </select>
                                            </div>
                                        </div>
    
                                        <button type="button" id="update-user-btn" class="btn app-btn-primary" >Submit</button>
                                    </form>
    
    `;
        };

        var accountUpdateForm = (accountobj) => {

            return `

                <div class="row g-4 settings-section">
	                <div class="col-12 col-md-4">
		                <h3 class="section-title">Account details</h3>
		                <div class="section-intro">View account details </div>
	                </div>
	                <div class="col-12 col-md-8">
		                <div class="app-card app-card-modal app-card-settings shadow-sm p-4">
						    
						    <div class="app-card-body">
                                <div class="mb-2"><strong>Name:</strong>${accountobj.name}</div>
                                <div class="mb-2"><strong>Status:</strong> <span class="badge bg-success">Active</span></div>
							    <div class="mb-2"><strong>Current limit:</strong> ${accountobj.limit}</div>
                                <div class="mb-2"><strong>Opening balance:</strong> ${accountobj.ob}</div>
                                <div class="mb-2"><strong>Current balance:</strong> ${accountobj.cb}</div>
							    <div class="mb-2"><strong>Automatically resets at:</strong> midnight</div>
							    <div class="row justify-content-between">
								    <div class="col-auto invisible">
								        <a class="btn app-btn-primary" href="#">Hidden</a>
								    </div>
								    <div class="col-auto">
								        <a id="toggle-adjust-balances" class="btn app-btn-secondary" href="#"> <i data-feather="edit"></i> Adjust</a>
								    </div>
							    </div>
								    
						    </div><!--//app-card-body-->
						    
						</div><!--//app-card-->
	                </div>
                </div><!--//row-->


                <div id="adjust-balances" class="row g-4 settings-section d-none">
	                <div class="col-12 col-md-4">
		                <h3 class="section-title">Adjust Balance &amp; Limits</h3>
		                <div class="section-intro">Balance & account limit adjustment</div>
	                </div>
	                <div class="col-12 col-md-8">
		                <div class="app-card app-card-modal app-card-settings shadow-sm p-4">						    
						    <div class="app-card-body">
							    <form class="settings-form">
                                    <div class=row mb-3>
                                        <div class="mb-3 col-6">
                                            <label for="account-update-balance" class="form-label">Update current balance<span class="ms-2" data-bs-container="body" data-bs-toggle="popover" data-bs-trigger="hover focus"  data-bs-placement="top" data-bs-content="Adjust current operating balance"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                                <path d="M8.93 6.588l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588z"/>
                                                <circle cx="8" cy="4.5" r="1"/>
                                                </svg></span></label>
                                            <input type="text" class="form-control" id="account-update-balance" value="${accountobj.cb}" required>
                                        </div>

                                        <input type="hidden" class="form-control" id="account-update-id" value="${accountobj.id}">

                                        <div class="col-6 mb-3">
                                            <label for="account-update-limit" class="form-label">Adjust limit</label>
                                            <input type="text" class="form-control" id="account-update-limit" value="${accountobj.limit}" required>
                                        </div>

                                    </div>


									<div class="mt-3">
                                        <button type="button" id="update-account-btn" class="btn app-btn-primary" >Submit</button>
									</div>
							    </form>
						    </div><!--//app-card-body-->						    
						</div><!--//app-card-->
	                </div>
                </div><!--//row-->
        
        `;
            };


            var requestUpdateForm = (requestobj) => {

                return `
    
                    <div class="row g-4 settings-section">
                        <div class="col-12 col-md-4">
                            <h3 class="section-title">Cash Collection request details</h3>
                            <div class="section-intro">View request details </div>
                        </div>
                        <div class="col-12 col-md-8">
                            <div class="app-card app-card-modal app-card-settings shadow-sm p-4">
                                
                                <div class="app-card-body">
                                    <div class="mb-2"><strong>Code: </strong> #00${requestobj.id}</div>
                                    <div class="mb-2"><strong>Status: </strong> ${requestobj.status}</div>
                                    <div class="mb-2"><strong>Type: </strong> ${requestobj.purpose}</div>
                                    <div class="mb-2"><strong>Cash amount: </strong> ${requestobj.amount}</div>
                                    <div class="mb-2"><strong>Posted on: </strong> ${requestobj.date}</div>
                                    <div class="mb-2"><strong>Posted by: </strong> ${requestobj.by}</div>

                                    <input type="hidden" class="form-control" id="request-update-id" value="${requestobj.id}">

                                    <div class="row justify-content-between">
                                        <div class="col-auto invisible">
                                            <a class="btn app-btn-primary" href="#">Hidden</a>
                                        </div>
                                        <div class="col-auto">
                                            <a id="update-request-btn" class="btn app-btn-secondary" href="#"> <i data-feather="thumbs-up"></i> Accept request</a>
                                        </div>
                                    </div>
                                        
                                </div><!--//app-card-body-->
                                
                            </div><!--//app-card-->
                        </div>
                    </div><!--//row-->
            
            `;
                };


    var floatUpdateForm = (transobj) => {

                    return `
        
                        <div class="row g-4 settings-section">
                            <div class="col-12 col-md-4">
                                <h3 class="section-title">Transaction details</h3>
                                <div class="section-intro">View transaction details </div>
                            </div>
                            <div class="col-12 col-md-8">
                                <div class="app-card app-card-modal app-card-settings shadow-sm p-4">
                                    
                                    <div class="app-card-body">
                                        <div class="mb-2"><strong>Code: </strong> #00${transobj.id}</div>
                                        <div class="mb-2"><strong>Status: </strong> ${transobj.status}</div>
                                        <div class="mb-2"><strong>Type: </strong> ${transobj.purpose}</div>
                                        <div class="mb-2"><strong>Cash amount: </strong> ${transobj.amount}</div>
                                        <div class="mb-2"><strong>Posted on: </strong> ${transobj.date}</div>
                                        <div class="mb-2"><strong>Posted by: </strong> ${transobj.by}</div>
    
                                        <input type="hidden" class="form-control" id="float-update-id" value="${transobj.id}">
    
                                        <div class="row justify-content-between">
                                            <div class="col-auto invisible">
                                                <a class="btn app-btn-primary" href="#">Hidden</a>
                                            </div>
                                            <div class="col-auto">
                                                <a id="update-float-btn" class="btn app-btn-secondary" href="#"> <i data-feather="thumbs-up"></i> approve transaction</a>
                                            </div>
                                        </div>
                                            
                                    </div><!--//app-card-body-->
                                    
                                </div><!--//app-card-->
                            </div>
                        </div><!--//row-->
                
                `;
                    };
    

var cashTemplate = `
		
<div class="row g-3 mb-4 align-items-center justify-content-between">
    <div class="col-auto">
        <h1 class="app-page-title mb-0">Cash Collection Requests</h1>
    </div>

    <div class="col-auto">
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">

<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#requestModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    post collection request
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="requests-table-tab" class="requests-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="requests-all-tab" data-bs-toggle="tab" href="#requests-all" role="tab" aria-controls="requests-all" aria-selected="true">All</a>
<a class="flex-sm-fill text-sm-center nav-link"  id="requests-pending-tab" data-bs-toggle="tab" href="#requests-pending" role="tab" aria-controls="requests-pending" aria-selected="false">Pending</a>
<a class="flex-sm-fill text-sm-center nav-link" id="requests-accepted-tab" data-bs-toggle="tab" href="#requests-accepted" role="tab" aria-controls="requests-accepted" aria-selected="false">Accepted</a>
<a class="flex-sm-fill text-sm-center nav-link d-none" id="requests-delivered-tab" data-bs-toggle="tab" href="#requests-delivered" role="tab" aria-controls="requests-delivered" aria-selected="false">Upcoming</a>
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
                        <div id="requests-pending-table" class="ps-4 pe-4 table-responsive">
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
                        <div id="requests-accepted-table" class="ps-4 pe-4 table-responsive">
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
                        <div id="requests-delivered-table" class="ps-4 pe-4 table-responsive">
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
                        <div id="requests-all-table" class="ps-4 pe-4 table-responsive">
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
        <h1 class="app-page-title mb-0">Float purchases & Returns</h1>
    </div>


    <div class="col-auto">
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">

<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">

            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#"  data-bs-toggle="modal" data-bs-target="#floatModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    Post transaction
                </a>
            </div>

        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="floats-table-tab" class="floats-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="floats-all-tab" data-bs-toggle="tab" href="#floats-all" role="tab" aria-controls="floats-all" aria-selected="true">All transactions</a>
<a class="flex-sm-fill text-sm-center nav-link" id="floats-pending-tab" data-bs-toggle="tab" href="#floats-pending" role="tab" aria-controls="floats-pending" aria-selected="false">Pending transactions</a>
<a class="flex-sm-fill text-sm-center nav-link" id="floats-confirmed-tab" data-bs-toggle="tab" href="#floats-confirmed" role="tab" aria-controls="floats-confirmed" aria-selected="false">Confirmed transactions</a>
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
    <h1 class="app-page-title mb-0">Roles & Permissions</h1>
</div>

    <div class="col-auto">
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">

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
                                <div id="roles-all-table" class="ps-4 pe-4 table-responsive">
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
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">


<div class="col-auto">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#userModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    Add new user
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="user-table-tab" class="floats-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="users-all-tab" data-bs-toggle="tab" href="#users-all" role="tab" aria-controls="users-all" aria-selected="true">All users</a>
<a class="flex-sm-fill text-sm-center nav-link d-none" id="users-pending-tab" data-bs-toggle="tab" href="#users-pending" role="tab" aria-controls="users-pending" aria-selected="false">Non-members</a>
<a class="flex-sm-fill text-sm-center nav-link d-none" id="users-confirmed-tab" data-bs-toggle="tab" href="#users-confirmed" role="tab" aria-controls="users-confirmed" aria-selected="false">Members</a>
</nav>

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
                        <div id="users-all-table" class="table-responsive ms-4 me-4">
                        </div>
                    </div>
                </div>
            </div><!--//app-card-body-->		
        </div><!--//app-card-->						
    </div><!--//tab-pane-->



    <div class="tab-pane fade" id="users-pending" role="tabpanel" aria-labelledby="users-pending-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="users-pending-table" class="ps-4 pe-4 table-responsive">
                            </div>
                        </div>
                    </div>

                </div><!--//app-card-body-->		
            </div><!--//app-card-->	
    </div><!--//tab-pane-->

    <div class="tab-pane fade show active" id="users-confirmed" role="tabpanel" aria-labelledby="users-all-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="users-confirmed-table" class="ps-4 pe-4 table-responsive">
                            </div>
                        </div>
                    </div>

                </div><!--//app-card-body-->		
            </div><!--//app-card-->	
    </div><!--//tab-pane-->

</div>

`

var accountTemplate = `
<div class="row g-3 mb-4 align-items-center justify-content-between">
<div class="col-auto">
    <h1 class="app-page-title mb-0">Account Management</h1>
</div>

    <div class="col-auto">
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">


<div class="col-auto d-none">
     <div class="page-utilities">
        <div class="row g-2 justify-content-start justify-content-md-end align-items-center">
            <div class="col-auto">						    
                <a class="btn app-btn-secondary" href="#" data-bs-toggle="modal" data-bs-target="#userModal">
                    <i data-feather="plus" style="width: 16px; height: 16px;"></i>
                    Add new account
                </a>
            </div>
        </div><!--//row-->
    </div><!--//table-utilities-->
</div><!--//col-auto-->
</div><!--//row-->

<nav id="account-table-tab" class="floats-table-tab app-nav-tabs nav shadow-sm flex-column flex-sm-row mb-4">
<a class="flex-sm-fill text-sm-center nav-link active" id="accounts-all-tab" data-bs-toggle="tab" href="#accounts-all" role="tab" aria-controls="accounts-all" aria-selected="true">All accounts</a>
<a class="flex-sm-fill text-sm-center nav-link d-none" id="accounts-pending-tab" data-bs-toggle="tab" href="#accounts-pending" role="tab" aria-controls="accounts-pending" aria-selected="false">Non-members</a>
<a class="flex-sm-fill text-sm-center nav-link d-none" id="accounts-confirmed-tab" data-bs-toggle="tab" href="#accounts-confirmed" role="tab" aria-controls="accounts-confirmed" aria-selected="false">Members</a>
</nav>

<div class="tab-content" id="accounts-table-tab-content">

    <div id="accounts-spinner" class="d-flex justify-content-center d-none">
        <div class="spinner-border text-success m-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div class="tab-pane fade show active" id="accounts-all" role="tabpanel" aria-labelledby="accounts-all-tab">
            <div class="app-card app-card-requests-table mb-5">
            <div class="app-card-body">
                <div class="row">
                    <div class="col-lg-12 no-padding">
                        <div id="accounts-all-table" class="table-responsive ms-4 me-4">
                        </div>
                    </div>
                </div>
            </div><!--//app-card-body-->		
        </div><!--//app-card-->						
    </div><!--//tab-pane-->



    <div class="tab-pane fade" id="accounts-pending" role="tabpanel" aria-labelledby="accounts-pending-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="accounts-pending-table" class="ps-4 pe-4 table-responsive">
                            </div>
                        </div>
                    </div>

                </div><!--//app-card-body-->		
            </div><!--//app-card-->	
    </div><!--//tab-pane-->

    <div class="tab-pane fade show active" id="accounts-confirmed" role="tabpanel" aria-labelledby="accounts-all-tab">
            <div class="app-card app-card-requests-table mb-5">
                <div class="app-card-body">
                    <div class="row">
                        <div class="col-lg-12 no-padding">
                            <div id="accounts-confirmed-table" class="ps-4 pe-4 table-responsive">
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
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">
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

    <div class="col-auto">
        <span type="button" class="nav-icon home-btn">
            <i class="bold-icon" data-feather="x" style="width: 36px; height: 36px;"></i>
        </span>
    </div>
</div>

<div class="row g-3 mb-4 align-items-center justify-content-between">
</div><!--//row-->
<p class="fst-italic">Coming soon</p>
`

